"""FastAPI server for Claude Code Log web interface."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import json
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .parser import (
    load_transcript,
    load_directory_transcripts,
    filter_messages_by_date,
    extract_text_content,
)
from .renderer import (
    generate_html,
    generate_projects_index_html,
    TemplateMessage,
    TemplateProject,
    format_timestamp,
    render_message_content,
    escape_html,
)
from .cache import CacheManager, get_library_version
from .models import TranscriptEntry, AssistantTranscriptEntry, SummaryTranscriptEntry
from .utils import should_skip_message, is_command_message, create_session_preview

app = FastAPI(
    title="Claude Code Log API",
    description="API for processing and viewing Claude Code transcripts",
    version="0.1.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Svelte app) from svelte-viewer/dist
static_files_path = Path(__file__).parent.parent / "svelte-viewer" / "dist"
if static_files_path.exists():
    app.mount("/static", StaticFiles(directory=static_files_path), name="static")


# Response models
class ProcessedMessage(BaseModel):
    id: str
    type: str
    display_type: str
    content: str
    content_html: str
    timestamp: str
    formatted_timestamp: str
    css_class: str
    session_id: str
    session_summary: Optional[str] = None
    is_sidechain: bool = False
    token_usage: Optional[str] = None
    is_session_header: bool = False


class SessionInfo(BaseModel):
    id: str
    summary: Optional[str] = None
    first_timestamp: str
    last_timestamp: str
    timestamp_range: str
    message_count: int
    first_user_message: str
    token_summary: str
    total_input_tokens: int
    total_output_tokens: int
    total_cache_creation_tokens: int
    total_cache_read_tokens: int


class TranscriptData(BaseModel):
    messages: List[ProcessedMessage]
    sessions: List[SessionInfo]
    title: str
    library_version: str


class ProjectData(BaseModel):
    name: str
    display_name: str
    sessions: List[SessionInfo]
    total_messages: int
    total_sessions: int


@app.get("/")
async def read_root():
    """Serve the Svelte app."""
    if static_files_path.exists():
        return FileResponse(static_files_path / "index.html")
    return {"message": "Claude Code Log API", "status": "Svelte app not built"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/parse-files", response_model=TranscriptData)
async def parse_files(
    files: List[UploadFile] = File(...),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    title: Optional[str] = Query("Claude Transcript"),
):
    """Parse uploaded JSONL files and return processed transcript data."""
    try:
        all_entries: List[TranscriptEntry] = []

        # Process each uploaded file
        for file in files:
            if not file.filename or not file.filename.endswith(".jsonl"):
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} is not a JSONL file"
                )

            content = await file.read()

            # Save to temporary file and parse
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".jsonl", delete=False
            ) as temp_file:
                temp_file.write(content.decode("utf-8"))
                temp_path = Path(temp_file.name)

            try:
                # Parse the file using existing logic
                entries = load_transcript(temp_path, silent=True)
                all_entries.extend(entries)
            finally:
                # Clean up temp file
                temp_path.unlink(missing_ok=True)

        # Apply date filtering if specified
        if from_date or to_date:
            all_entries = filter_messages_by_date(all_entries, from_date, to_date)

        # Sort chronologically
        all_entries.sort(key=lambda e: getattr(e, "timestamp", ""))

        # Process entries into UI-friendly format
        processed_data = process_entries_for_api(
            all_entries, title or "Uploaded Transcript"
        )

        return processed_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process files: {str(e)}"
        )


@app.post("/api/parse-directory", response_model=TranscriptData)
async def parse_directory_path(
    directory_path: str,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
):
    """Parse JSONL files from a local directory path."""
    try:
        dir_path = Path(directory_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Directory does not exist")

        cache_manager = CacheManager(dir_path, get_library_version())
        entries = load_directory_transcripts(
            dir_path, cache_manager, from_date, to_date, silent=True
        )

        processed_data = process_entries_for_api(
            entries, f"Transcript - {dir_path.name}"
        )
        return processed_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process directory: {str(e)}"
        )


@app.get("/api/projects", response_model=List[ProjectData])
async def get_projects():
    """Get all projects from ~/.claude/projects/."""
    try:
        projects_dir = Path.home() / ".claude" / "projects"
        if not projects_dir.exists():
            return []

        projects = []
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith("."):
                try:
                    cache_manager = CacheManager(project_dir, get_library_version())
                    entries = load_directory_transcripts(
                        project_dir, cache_manager, silent=True
                    )

                    if entries:
                        processed_data = process_entries_for_api(
                            entries, project_dir.name
                        )
                        projects.append(
                            ProjectData(
                                name=project_dir.name,
                                display_name=processed_data.title,
                                sessions=processed_data.sessions,
                                total_messages=len(processed_data.messages),
                                total_sessions=len(processed_data.sessions),
                            )
                        )
                except Exception as e:
                    print(f"Error processing project {project_dir.name}: {e}")
                    continue

        return projects

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


def process_entries_for_api(
    entries: List[TranscriptEntry], title: str
) -> TranscriptData:
    """Process transcript entries into API response format."""
    from .cache import get_library_version

    # Build session summaries mapping (same logic as renderer.py)
    session_summaries: Dict[str, str] = {}
    uuid_to_session: Dict[str, str] = {}

    # Build mapping from message UUID to session ID
    for entry in entries:
        if hasattr(entry, "uuid") and hasattr(entry, "sessionId"):
            entry_uuid = getattr(entry, "uuid", "")
            session_id = getattr(entry, "sessionId", "")
            if entry_uuid and session_id:
                if isinstance(entry, AssistantTranscriptEntry):
                    uuid_to_session[entry_uuid] = session_id

    # Map summaries to sessions
    for entry in entries:
        if isinstance(entry, SummaryTranscriptEntry):
            leaf_uuid = entry.leafUuid
            if leaf_uuid in uuid_to_session:
                session_summaries[uuid_to_session[leaf_uuid]] = entry.summary

    # Track sessions and messages
    sessions: Dict[str, SessionInfo] = {}
    messages: List[ProcessedMessage] = []
    seen_sessions: set[str] = set()
    seen_request_ids: set[str] = set()

    for entry in entries:
        if isinstance(entry, SummaryTranscriptEntry):
            continue

        session_id = getattr(entry, "sessionId", "unknown")
        timestamp = getattr(entry, "timestamp", "")
        formatted_timestamp = format_timestamp(timestamp) if timestamp else ""

        # Initialize session if not seen
        if session_id not in sessions:
            sessions[session_id] = SessionInfo(
                id=session_id,
                summary=session_summaries.get(session_id),
                first_timestamp=timestamp,
                last_timestamp=timestamp,
                timestamp_range="",
                message_count=0,
                first_user_message="",
                token_summary="",
                total_input_tokens=0,
                total_output_tokens=0,
                total_cache_creation_tokens=0,
                total_cache_read_tokens=0,
            )

            # Add session header
            if session_id not in seen_sessions:
                seen_sessions.add(session_id)
                session_title = (
                    f"{session_summaries.get(session_id)} • {session_id[:8]}"
                    if session_summaries.get(session_id)
                    else session_id[:8]
                )

                messages.append(
                    ProcessedMessage(
                        id=f"session-{session_id}",
                        type="session_header",
                        display_type="Session",
                        content=session_title,
                        content_html=escape_html(session_title),
                        timestamp=timestamp,
                        formatted_timestamp=formatted_timestamp,
                        css_class="session-header",
                        session_id=session_id,
                        session_summary=session_summaries.get(session_id),
                        is_session_header=True,
                    )
                )

        session = sessions[session_id]
        session.message_count += 1
        session.last_timestamp = timestamp

        # Process different entry types
        if entry.type == "user":
            content = extract_text_content(entry.message.content)  # type: ignore
            if should_skip_message(content):
                continue

            if not session.first_user_message and content.strip():
                session.first_user_message = create_session_preview(content)

            messages.append(
                ProcessedMessage(
                    id=getattr(entry, "uuid", f"user-{len(messages)}"),
                    type="user",
                    display_type="👤 User"
                    if not getattr(entry, "isSidechain", False)
                    else "📝 Sub-assistant prompt",
                    content=content,
                    content_html=f"<pre>{escape_html(content)}</pre>",
                    timestamp=timestamp,
                    formatted_timestamp=formatted_timestamp,
                    css_class="user"
                    + (" sidechain" if getattr(entry, "isSidechain", False) else ""),
                    session_id=session_id,
                    session_summary=session_summaries.get(session_id),
                    is_sidechain=getattr(entry, "isSidechain", False),
                )
            )

        elif entry.type == "assistant":
            assistant_entry = entry  # type: ignore
            usage = getattr(assistant_entry.message, "usage", None)
            request_id = getattr(assistant_entry, "requestId", None)
            token_usage_str: Optional[str] = None

            # Track token usage
            if usage and request_id and request_id not in seen_request_ids:
                seen_request_ids.add(request_id)

                if usage.input_tokens:
                    session.total_input_tokens += usage.input_tokens
                if usage.output_tokens:
                    session.total_output_tokens += usage.output_tokens
                if usage.cache_creation_input_tokens:
                    session.total_cache_creation_tokens += (
                        usage.cache_creation_input_tokens
                    )
                if usage.cache_read_input_tokens:
                    session.total_cache_read_tokens += usage.cache_read_input_tokens

                # Format token usage
                token_parts = []
                if usage.input_tokens:
                    token_parts.append(f"Input: {usage.input_tokens}")
                if usage.output_tokens:
                    token_parts.append(f"Output: {usage.output_tokens}")
                if usage.cache_creation_input_tokens:
                    token_parts.append(
                        f"Cache Creation: {usage.cache_creation_input_tokens}"
                    )
                if usage.cache_read_input_tokens:
                    token_parts.append(f"Cache Read: {usage.cache_read_input_tokens}")
                token_usage_str = " | ".join(token_parts)

            # Process message content
            content = render_message_content(
                assistant_entry.message.content, "assistant"
            )  # type: ignore

            messages.append(
                ProcessedMessage(
                    id=getattr(entry, "uuid", f"assistant-{len(messages)}"),
                    type="assistant",
                    display_type="🤖 Assistant"
                    if not getattr(entry, "isSidechain", False)
                    else "🔗 Sub-assistant",
                    content=extract_text_content(assistant_entry.message.content),  # type: ignore
                    content_html=content,
                    timestamp=timestamp,
                    formatted_timestamp=formatted_timestamp,
                    css_class="assistant"
                    + (" sidechain" if getattr(entry, "isSidechain", False) else ""),
                    session_id=session_id,
                    session_summary=session_summaries.get(session_id),
                    is_sidechain=getattr(entry, "isSidechain", False),
                    token_usage=token_usage_str,
                )
            )

    # Finalize session data
    for session in sessions.values():
        # Format timestamp range
        if session.first_timestamp and session.last_timestamp:
            if session.first_timestamp == session.last_timestamp:
                session.timestamp_range = format_timestamp(session.first_timestamp)
            else:
                session.timestamp_range = f"{format_timestamp(session.first_timestamp)} - {format_timestamp(session.last_timestamp)}"

        # Format token summary
        if session.total_input_tokens > 0 or session.total_output_tokens > 0:
            token_parts = []
            if session.total_input_tokens > 0:
                token_parts.append(f"Input: {session.total_input_tokens}")
            if session.total_output_tokens > 0:
                token_parts.append(f"Output: {session.total_output_tokens}")
            if session.total_cache_creation_tokens > 0:
                token_parts.append(
                    f"Cache Creation: {session.total_cache_creation_tokens}"
                )
            if session.total_cache_read_tokens > 0:
                token_parts.append(f"Cache Read: {session.total_cache_read_tokens}")
            session.token_summary = "Token usage – " + " | ".join(token_parts)

    return TranscriptData(
        messages=messages,
        sessions=list(sessions.values()),
        title=title,
        library_version=get_library_version(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
