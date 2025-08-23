#!/usr/bin/env python3
"""Parse and extract data from Claude transcript JSONL files."""

import json
from pathlib import Path
import re
from typing import Any, List, Optional, Union, TYPE_CHECKING, Dict
from datetime import datetime
import dateparser

from .models import (
    TranscriptEntry,
    SummaryTranscriptEntry,
    parse_transcript_entry,
    ContentItem,
    TextContent,
    ThinkingContent,
    ToolUseContent,
    ToolResultContent,
    ImageContent,
    Span,
)

if TYPE_CHECKING:
    from .cache import CacheManager


def extract_text_content(content: Union[str, List[ContentItem], None]) -> str:
    """Extract text content from Claude message content structure (supports both custom and Anthropic types)."""
    if content is None:
        return ""
    if isinstance(content, list):
        text_parts: List[str] = []
        for item in content:
            # Handle both custom TextContent and official Anthropic TextBlock
            if isinstance(item, TextContent):
                text_parts.append(item.text)
            elif (
                hasattr(item, "type")
                and hasattr(item, "text")
                and getattr(item, "type") == "text"
            ):
                # Official Anthropic TextBlock
                text_parts.append(getattr(item, "text"))
            elif isinstance(item, ThinkingContent):
                # Skip thinking content in main text extraction
                continue
            elif hasattr(item, "type") and getattr(item, "type") == "thinking":
                # Skip official Anthropic thinking content too
                continue
        return "\n".join(text_parts)
    else:
        return str(content) if content else ""


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def filter_messages_by_date(
    messages: List[TranscriptEntry], from_date: Optional[str], to_date: Optional[str]
) -> List[TranscriptEntry]:
    """Filter messages based on date range."""
    if not from_date and not to_date:
        return messages

    # Parse the date strings using dateparser
    from_dt = None
    to_dt = None

    if from_date:
        from_dt = dateparser.parse(from_date)
        if not from_dt:
            raise ValueError(f"Could not parse from-date: {from_date}")
        # If parsing relative dates like "today", start from beginning of day
        if from_date in ["today", "yesterday"] or "days ago" in from_date:
            from_dt = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    if to_date:
        to_dt = dateparser.parse(to_date)
        if not to_dt:
            raise ValueError(f"Could not parse to-date: {to_date}")
        # If parsing relative dates like "today", end at end of day
        if to_date in ["today", "yesterday"] or "days ago" in to_date:
            to_dt = to_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    filtered_messages: List[TranscriptEntry] = []
    for message in messages:
        # Handle SummaryTranscriptEntry which doesn't have timestamp
        if isinstance(message, SummaryTranscriptEntry):
            filtered_messages.append(message)
            continue

        timestamp_str = message.timestamp
        if not timestamp_str:
            continue

        message_dt = parse_timestamp(timestamp_str)
        if not message_dt:
            continue

        # Convert to naive datetime for comparison (dateparser returns naive datetimes)
        if message_dt.tzinfo:
            message_dt = message_dt.replace(tzinfo=None)

        # Check if message falls within date range
        if from_dt and message_dt < from_dt:
            continue
        if to_dt and message_dt > to_dt:
            continue

        filtered_messages.append(message)

    return filtered_messages


def _has_tool_activity(content: Union[str, List[ContentItem], None]) -> bool:
    """Detect whether message content includes tool use or tool result or images/thinking."""
    if not content or isinstance(content, str):
        return False
    for item in content:
        item_type = getattr(item, "type", None)
        if isinstance(item, (ToolUseContent, ToolResultContent, ThinkingContent, ImageContent)) or item_type in (
            "tool_use",
            "tool_result",
            "thinking",
            "image",
        ):
            return True
    return False


def _contains_todowrite(content: Union[str, List[ContentItem], None]) -> bool:
    if not content or isinstance(content, str):
        return False
    for item in content:
        if isinstance(item, ToolUseContent) and item.name == "TodoWrite":
            return True
        if hasattr(item, "type") and getattr(item, "type") == "tool_use":
            name = getattr(item, "name", "")
            if name == "TodoWrite":
                return True
    return False


def group_messages_into_spans(
    messages: List[TranscriptEntry], gap_seconds: int = 600
) -> List[Span]:
    """Group messages into logical spans using simple, conservative heuristics.

    Heuristics:
    - New span when session changes
    - New span when time gap between adjacent messages exceeds gap_seconds
    - Span kind classification based on presence of TodoWrite/tool activity/system-only
    - Title derived from first user message text in span, else assistant text
    """
    spans: List[Span] = []
    if not messages:
        return spans

    # Work on non-summary messages to align with renderer iteration
    seq = [m for m in messages if not isinstance(m, SummaryTranscriptEntry)]
    if not seq:
        return spans

    def get_dt(idx: int) -> Optional[datetime]:
        m = seq[idx]
        ts = getattr(m, "timestamp", None)
        return parse_timestamp(ts) if ts else None

    def start_new_span(start_idx: int) -> Dict[str, Any]:
        m = seq[start_idx]
        return {
            "start_index": start_idx,
            "end_index": start_idx,
            "message_indices": [start_idx],
            "session_id": getattr(m, "sessionId", None),
            "start_timestamp": getattr(m, "timestamp", None),
            "end_timestamp": getattr(m, "timestamp", None),
            "kind": "unknown",
            "title": None,
            "has_tooling": False,
            "has_todo": False,
            "all_system": True,
        }

    cur = start_new_span(0)

    def fold_message(i: int) -> None:
        m = messages[i]
        cur["end_index"] = i
        cur["message_indices"].append(i)
        cur["end_timestamp"] = getattr(m, "timestamp", None)

        # track flags
        content = getattr(getattr(m, "message", None), "content", None)
        if _has_tool_activity(content):
            cur["has_tooling"] = True
        if _contains_todowrite(content):
            cur["has_todo"] = True
        if getattr(m, "type", "") != "system":
            cur["all_system"] = False

        # title: first meaningful user text; fallback to assistant
        if cur.get("title") is None:
            text = extract_text_content(content)
            if getattr(m, "type", "") == "user" and text.strip():
                cur["title"] = text.strip().splitlines()[0][:120]
        if cur.get("title") is None and getattr(m, "type", "") == "assistant":
            text = extract_text_content(content)
            if text.strip():
                cur["title"] = text.strip().splitlines()[0][:120]

    def finalize_current_span() -> None:
        # compute kind
        kind: str
        if cur["has_todo"]:
            kind = "todo"
        elif cur["has_tooling"]:
            kind = "tooling"
        elif cur["all_system"]:
            kind = "system"
        else:
            kind = "chat"

        span_id = f"{cur['session_id'] or 'span'}-{cur['start_index']}-{cur['end_index']}"

        spans.append(
            Span(
                id=span_id,
                title=cur.get("title"),
                kind=kind,  # type: ignore[arg-type]
                start_index=cur["start_index"],
                end_index=cur["end_index"],
                message_indices=list(cur["message_indices"]),
                start_timestamp=cur.get("start_timestamp"),
                end_timestamp=cur.get("end_timestamp"),
                session_id=cur.get("session_id"),
            )
        )

    # initialize with first message processed
    fold_message(0)

    for i in range(1, len(seq)):
        prev_dt = get_dt(i - 1)
        cur_dt = get_dt(i)
        prev_sess = getattr(seq[i - 1], "sessionId", None)
        cur_sess = getattr(seq[i], "sessionId", None)

        boundary = False
        if prev_sess != cur_sess:
            boundary = True
        elif prev_dt and cur_dt:
            delta = (cur_dt - prev_dt).total_seconds()
            if delta > gap_seconds:
                boundary = True

        if boundary:
            finalize_current_span()
            cur = start_new_span(i)
            fold_message(i)
        else:
            fold_message(i)

    # finalize last span
    finalize_current_span()

    return spans


def load_transcript(
    jsonl_path: Path,
    cache_manager: Optional["CacheManager"] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    silent: bool = False,
) -> List[TranscriptEntry]:
    """Load and parse JSONL transcript file, using cache if available."""
    # Try to load from cache first
    if cache_manager is not None:
        # Use filtered loading if date parameters are provided
        if from_date or to_date:
            cached_entries = cache_manager.load_cached_entries_filtered(
                jsonl_path, from_date, to_date
            )
        else:
            cached_entries = cache_manager.load_cached_entries(jsonl_path)

        if cached_entries is not None:
            if not silent:
                print(f"Loading {jsonl_path} from cache...")
            return cached_entries

    # Parse from source file
    messages: List[TranscriptEntry] = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        if not silent:
            print(f"Processing {jsonl_path}...")
        for line_no, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    entry_dict: dict[str, Any] | str = json.loads(line)
                    if not isinstance(entry_dict, dict):
                        print(
                            f"Line {line_no} of {jsonl_path} is not a JSON object: {line}"
                        )
                        continue

                    entry_type: str | None = entry_dict.get("type")

                    if entry_type in ["user", "assistant", "summary", "system"]:
                        # Parse using Pydantic models
                        entry = parse_transcript_entry(entry_dict)
                        messages.append(entry)
                    else:
                        print(
                            f"Line {line_no} of {jsonl_path} is not a recognised message type: {line}"
                        )
                except json.JSONDecodeError as e:
                    print(
                        f"Line {line_no} of {jsonl_path} | JSON decode error: {str(e)}"
                    )
                except ValueError as e:
                    # Extract a more descriptive error message
                    error_msg = str(e)
                    if "validation error" in error_msg.lower():
                        err_no_url = re.sub(
                            r"    For further information visit https://errors.pydantic(.*)\n?",
                            "",
                            error_msg,
                        )
                        print(f"Line {line_no} of {jsonl_path} | {err_no_url}")
                    else:
                        print(
                            f"Line {line_no} of {jsonl_path} | ValueError: {error_msg}"
                            "\n{traceback.format_exc()}"
                        )
                except Exception as e:
                    print(
                        f"Line {line_no} of {jsonl_path} | Unexpected error: {str(e)}"
                        "\n{traceback.format_exc()}"
                    )

    # Save to cache if cache manager is available
    if cache_manager is not None:
        cache_manager.save_cached_entries(jsonl_path, messages)

    return messages


def load_directory_transcripts(
    directory_path: Path,
    cache_manager: Optional["CacheManager"] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    silent: bool = False,
) -> List[TranscriptEntry]:
    """Load all JSONL transcript files from a directory and combine them."""
    all_messages: List[TranscriptEntry] = []

    # Find all .jsonl files
    jsonl_files = list(directory_path.glob("*.jsonl"))

    for jsonl_file in jsonl_files:
        messages = load_transcript(
            jsonl_file, cache_manager, from_date, to_date, silent
        )
        all_messages.extend(messages)

    # Sort all messages chronologically
    def get_timestamp(entry: TranscriptEntry) -> str:
        if hasattr(entry, "timestamp"):
            return entry.timestamp  # type: ignore
        return ""

    all_messages.sort(key=get_timestamp)
    return all_messages
