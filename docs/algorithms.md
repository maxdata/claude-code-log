# Algorithm Documentation - claude-code-log

## Repository Overview

**claude-code-log** is a Python CLI tool that converts Claude Code transcript JSONL files into readable HTML format. It provides interactive TUI interface, project hierarchy processing, and advanced caching mechanisms for performance optimization.

**Main Purpose**: Transform Claude Code session logs into searchable, filterable HTML transcripts with project-level organization, timeline navigation, and token usage tracking.

**Programming Languages**: Python (primary), HTML/CSS/JavaScript (frontend)

## Algorithm Categories

### 1. Data Parsing & Validation Algorithms
### 2. Caching & Performance Optimization Algorithms  
### 3. Date & Time Processing Algorithms
### 4. HTML Rendering & Template Processing Algorithms
### 5. File System & Directory Management Algorithms
### 6. Content Filtering & Search Algorithms

---

## Individual Algorithms

### 1. Data Parsing & Validation Algorithms

#### JSONL Line-by-Line Parser Algorithm
**File**: `claude_code_log/parser.py`  
**Lines**: 123-196

**Description**: Parses Claude transcript JSONL files with robust error handling and type validation using Pydantic models.

**Key Operations**:
```python
def load_transcript(jsonl_path: Path, cache_manager: Optional["CacheManager"] = None, 
                   from_date: Optional[str] = None, to_date: Optional[str] = None, 
                   silent: bool = False) -> List[TranscriptEntry]:
    messages: List[TranscriptEntry] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    entry_dict = json.loads(line)
                    entry_type = entry_dict.get("type")
                    if entry_type in ["user", "assistant", "summary", "system"]:
                        entry = parse_transcript_entry(entry_dict)
                        messages.append(entry)
                except json.JSONDecodeError as e:
                    # Handle malformed JSON gracefully
                except ValueError as e:
                    # Handle Pydantic validation errors
```

**Time Complexity**: O(n) where n is the number of lines in JSONL file  
**Space Complexity**: O(m) where m is the number of valid transcript entries

#### Content Structure Extraction Algorithm
**File**: `claude_code_log/parser.py`  
**Lines**: 24-50

**Description**: Extracts text content from Claude's nested content structures, handling multiple content types (text, thinking, tool use).

**Key Operations**:
```python
def extract_text_content(content: Union[str, List[ContentItem], None]) -> str:
    if isinstance(content, list):
        text_parts: List[str] = []
        for item in content:
            if isinstance(item, TextContent):
                text_parts.append(item.text)
            elif hasattr(item, "type") and getattr(item, "type") == "text":
                text_parts.append(getattr(item, "text"))
            elif isinstance(item, ThinkingContent):
                continue  # Skip thinking content in main extraction
        return "\n".join(text_parts)
```

**Time Complexity**: O(k) where k is the number of content items  
**Space Complexity**: O(k) for storing text parts

#### Directory Transcript Aggregation Algorithm  
**File**: `claude_code_log/parser.py`  
**Lines**: 199-226

**Description**: Loads multiple JSONL files from a directory and combines them chronologically.

**Key Operations**:
- Directory globbing for `*.jsonl` files
- Individual file parsing with cache support
- Chronological sorting across all sessions
- Timestamp-based message ordering

**Time Complexity**: O(f * n + m log m) where f is files, n is average entries per file, m is total entries  
**Space Complexity**: O(m) for all combined messages

### 2. Caching & Performance Optimization Algorithms

#### Timestamp-Indexed Cache Structure Algorithm
**File**: `claude_code_log/cache.py`  
**Lines**: 273-328

**Description**: Creates timestamp-keyed cache structure for efficient date-range filtering without full file parsing.

**Key Operations**:
```python
def save_cached_entries(self, jsonl_path: Path, entries: List[TranscriptEntry]) -> None:
    cache_data: Dict[str, Any] = {}
    for entry in entries:
        timestamp = getattr(entry, "timestamp", "") if hasattr(entry, "timestamp") else ""
        if not timestamp:
            timestamp = "_no_timestamp"  # Special key for summaries
        
        if timestamp not in cache_data:
            cache_data[timestamp] = []
        cache_data[timestamp].append(entry.model_dump())
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)
```

**Time Complexity**: O(n) for cache creation, O(k) for filtered retrieval where k is matching entries  
**Space Complexity**: O(n) for full cache, O(k) for filtered results

#### Cache Invalidation & Version Compatibility Algorithm
**File**: `claude_code_log/cache.py`  
**Lines**: 411-452

**Description**: Implements sophisticated cache version compatibility checking to avoid unnecessary cache rebuilds.

**Key Operations**:
```python
def _is_cache_version_compatible(self, cache_version: str) -> bool:
    breaking_changes: dict[str, str] = {
        # Format: "cache_version": "minimum_library_version_required"
    }
    
    cache_ver = version.parse(cache_version)
    current_ver = version.parse(self.library_version)
    
    for breaking_version_pattern, min_required in breaking_changes.items():
        if current_ver >= version.parse(min_required):
            if breaking_version_pattern.endswith(".x"):
                major_minor = breaking_version_pattern[:-2]
                if str(cache_ver).startswith(major_minor):
                    return False
    return True
```

**Time Complexity**: O(b) where b is the number of breaking change rules  
**Space Complexity**: O(1)

#### File Modification Time Tracking Algorithm
**File**: `claude_code_log/cache.py`  
**Lines**: 135-155

**Description**: Tracks source file modification times to determine cache validity without expensive file parsing.

**Key Operations**:
- Source file `stat()` comparison with cached `mtime`
- Cache file existence verification
- 1-second tolerance for filesystem precision differences
- Automatic cache invalidation on source changes

**Time Complexity**: O(1) per file check  
**Space Complexity**: O(1)

### 3. Date & Time Processing Algorithms

#### Natural Language Date Parsing Algorithm
**File**: `claude_code_log/parser.py`  
**Lines**: 60-115

**Description**: Converts natural language date expressions into datetime objects with intelligent boundary handling.

**Key Operations**:
```python
def filter_messages_by_date(messages: List[TranscriptEntry], 
                           from_date: Optional[str], to_date: Optional[str]) -> List[TranscriptEntry]:
    from_dt = dateparser.parse(from_date) if from_date else None
    to_dt = dateparser.parse(to_date) if to_date else None
    
    # Smart boundary adjustment for relative dates
    if from_date in ["today", "yesterday"] or "days ago" in from_date:
        from_dt = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if to_date in ["today", "yesterday"] or "days ago" in to_date:
        to_dt = to_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
```

**Time Complexity**: O(n) where n is the number of messages to filter  
**Space Complexity**: O(k) where k is the number of messages within date range

#### ISO Timestamp Normalization Algorithm
**File**: `claude_code_log/parser.py`  
**Lines**: 52-57

**Description**: Normalizes ISO timestamp strings to datetime objects, handling timezone variations.

**Key Operations**:
```python
def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
```

**Time Complexity**: O(1) per timestamp  
**Space Complexity**: O(1)

#### Cached Date Range Filtering Algorithm
**File**: `claude_code_log/cache.py`  
**Lines**: 185-271

**Description**: Efficiently filters cached entries by timestamp keys without deserializing all data.

**Key Operations**:
- Timestamp key iteration over cache structure
- Selective deserialization of matching time ranges
- Special handling for entries without timestamps (`_no_timestamp`)
- Efficient skip logic for out-of-range timestamps

**Time Complexity**: O(t + k) where t is timestamp keys, k is matching entries  
**Space Complexity**: O(k) for filtered results

### 4. HTML Rendering & Template Processing Algorithms

#### Collapsible Content Generation Algorithm  
**File**: `claude_code_log/renderer.py`  
**Lines**: 136-168

**Description**: Creates expandable HTML details elements with content preview for long text blocks.

**Key Operations**:
```python
def create_collapsible_details(summary: str, content: str, css_classes: str = "") -> str:
    if len(content) <= 200:
        return f'<div class="details-content">{content}</div>'
    
    preview_text = content[:200] + "..."
    return f'''
    <details class="collapsible-details">
        <summary>
            {summary}
            <div class="preview-content">{preview_text}</div>
        </summary>
        <div class="details-content">{content}</div>
    </details>
    '''
```

**Time Complexity**: O(1) for short content, O(k) where k is preview length for long content  
**Space Complexity**: O(k) for preview text

#### Markdown to HTML Conversion Algorithm
**File**: `claude_code_log/renderer.py`  
**Lines**: 171-186

**Description**: Converts markdown content to HTML using mistune with GitHub-flavored extensions.

**Key Operations**:
```python
def render_markdown(text: str) -> str:
    renderer = mistune.create_markdown(
        plugins=["strikethrough", "footnotes", "table", "url", "task_lists", "def_list"],
        escape=False
    )
    return str(renderer(text))
```

**Time Complexity**: O(n) where n is the length of markdown text  
**Space Complexity**: O(n) for rendered HTML

#### Version-Based HTML Regeneration Algorithm
**File**: `claude_code_log/renderer.py`  
**Lines**: 66-107

**Description**: Checks HTML file version comments to determine if regeneration is needed.

**Key Operations**:
- HTML file version comment extraction
- Current library version comparison
- Selective file regeneration based on version mismatch
- Fallback to full regeneration if version cannot be determined

**Time Complexity**: O(1) per file check (reads only first 5 lines)  
**Space Complexity**: O(1)

### 5. File System & Directory Management Algorithms

#### Project Name Resolution Algorithm
**File**: `claude_code_log/renderer.py`  
**Lines**: 38-64

**Description**: Resolves human-readable project names from Claude's encoded directory names using working directory hints.

**Key Operations**:
```python
def get_project_display_name(project_dir_name: str, working_directories: Optional[List[str]] = None) -> str:
    if working_directories:
        paths_with_indices = [(Path(wd), i) for i, wd in enumerate(working_directories)]
        # Sort by: 1) path depth (fewer parts = less nested), 2) recency (lower index = more recent)
        best_path, _ = min(paths_with_indices, key=lambda p: (len(p[0].parts), p[1]))
        return best_path.name
    else:
        # Fall back to converting encoded project directory name
        display_name = project_dir_name
        if display_name.startswith("-"):
            display_name = display_name[1:].replace("-", "/")
        return display_name
```

**Time Complexity**: O(w log w) where w is the number of working directories  
**Space Complexity**: O(w) for path list

#### Cache Directory Management Algorithm
**File**: `claude_code_log/cache.py`  
**Lines**: 69-89

**Description**: Manages cache directory creation and project cache initialization.

**Key Operations**:
- Cache directory creation with `mkdir(exist_ok=True)`
- Project cache loading with error recovery
- Empty cache initialization for new projects
- Version compatibility validation

**Time Complexity**: O(1) for directory operations  
**Space Complexity**: O(c) where c is the size of cache data

### 6. Content Filtering & Search Algorithms

#### Message Type Classification Algorithm
**File**: `claude_code_log/utils.py` (referenced but not shown in detail)

**Description**: Classifies messages into categories for filtering (user, assistant, system, tool use, etc.).

**Key Operations**:
- Message type detection from entry structure
- Content-based classification for special cases
- Tool use vs tool result differentiation
- System command vs regular system message distinction

**Time Complexity**: O(1) per message  
**Space Complexity**: O(1)

#### Session Summary Matching Algorithm  
**File**: Referenced in models but algorithm not fully shown

**Description**: Matches asynchronously generated session summaries to their original sessions across multiple files.

**Key Operations**:
- Session ID extraction and correlation
- Summary content relevance scoring
- Cross-session timestamp alignment
- Duplicate summary detection and resolution

**Time Complexity**: O(s * m) where s is sessions, m is messages per session  
**Space Complexity**: O(s) for session index

---

## Performance Characteristics Summary

| Algorithm Category | Time Complexity | Space Complexity | Scalability Notes |
|-------------------|-----------------|------------------|-------------------|
| Data Parsing | O(n) | O(n) | Linear with file size, robust error handling |
| Caching | O(n) create, O(k) retrieve | O(n) storage, O(k) results | Dramatic performance improvement for large datasets |
| Date Processing | O(n) filtering | O(k) results | Efficient date range queries via timestamp indexing |
| HTML Rendering | O(n) | O(n) | Template-based generation with content preview optimization |
| File Management | O(1) typical | O(1) | Fast directory operations with version compatibility |
| Content Filtering | O(n) | O(k) | JavaScript-enhanced runtime filtering |

**Key Optimization Techniques**:
- **Timestamp-indexed caching**: Enables O(k) date range filtering instead of O(n) full parsing
- **Lazy loading**: Cache entries loaded only when needed, not at startup
- **Version-aware cache invalidation**: Avoids unnecessary rebuilds while ensuring compatibility
- **Progressive HTML generation**: Large content collapsed by default with preview
- **Natural language date parsing**: User-friendly date filters with intelligent boundary detection
- **Selective file processing**: Only modified files are reprocessed using mtime comparison

The claude-code-log codebase demonstrates sophisticated caching algorithms and efficient data processing techniques optimized for handling large Claude Code transcript datasets with minimal latency and memory usage.