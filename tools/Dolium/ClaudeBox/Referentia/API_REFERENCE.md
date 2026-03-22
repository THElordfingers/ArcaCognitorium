# ClaudeBox API Reference

Complete method and property reference for the `ClaudeBox` class and all public types.

---

## ClaudeBox

```python
ClaudeBox(
    config_path=None,   # str | Path | None — path to claudebox.config.yaml
    *,
    api_key=None,       # str | None — override config
    model=None,         # str | None — override config
    system_prompt=None, # str | None — override config
    max_tokens=None,    # int | None — override config
    stream=None,        # bool | None — override config
)
```

---

### Sending Messages

---

#### `send()`

```python
box.send(
    content,                    # str | list[ContentBlock]
    *,
    session_id=None,            # str | None
    model=None,                 # str | None
    max_tokens=None,            # int | None
    temperature=None,           # float | None  (0.0–1.0)
    top_p=None,                 # float | None  (0.0–1.0)
    top_k=None,                 # int | None
    stop_sequences=None,        # list[str] | None
    system=None,                # str | None
    stream=None,                # bool | None
    tools=None,                 # list[str] | None  (tool names to enable)
    tool_choice=None,           # str | None  ("auto"|"any"|"none"|tool_name)
    thinking_enabled=None,      # bool | None
    thinking_budget_tokens=None,# int | None
    metadata=None,              # dict[str, str] | None
    service_tier=None,          # str | None
    betas=None,                 # list[str] | None
    prefill=None,               # str | None
    **extra_kwargs,             # passed directly to API
) -> ClaudeResponse
```

Fires: `request_start`, `token`\*, `stream_start`\*, `stream_end`\*, `tool_call`\*, `tool_result`\*, `response`, `text`, `thinking`\*, `token_usage`, `request_end`

---

#### `send_async()`

Same signature as `send()`. Returns `Awaitable[ClaudeResponse]`.

---

#### `send_threaded()`

```python
box.send_threaded(
    content,                    # str | list[ContentBlock]
    *,
    on_token=None,              # Callable[[StreamToken], None] | None
    on_complete=None,           # Callable[[ClaudeResponse], None] | None
    on_error=None,              # Callable[[Exception], None] | None
    session_id=None,            # str | None
    **kwargs,                   # forwarded to send()
) -> threading.Thread
```

Returns immediately. Runs `send()` in a daemon thread.

---

#### `stream()`

```python
box.stream(
    content,        # str | list[ContentBlock]
    *,
    session_id=None,
    **kwargs,       # forwarded to send()
) -> Iterator[str]
```

Sync generator that yields text token strings one at a time.

---

#### `stream_async()`

```python
box.stream_async(
    content,        # str | list[ContentBlock]
    *,
    session_id=None,
    **kwargs,
) -> AsyncIterator[str]
```

Async generator that yields text token strings one at a time.

---

### Token Counting

---

#### `count_tokens()`

```python
box.count_tokens(
    content,            # str | list[ContentBlock]
    *,
    session_id=None,    # str | None  (uses session history)
    system=None,        # str | None
    tools=None,         # list[str] | None
    model=None,         # str | None
) -> int
```

Returns estimated input token count. Does not send a message.

---

### Sessions

---

#### `create_session()`

```python
box.create_session(
    session_id,             # str
    *,
    system_prompt=None,     # str | None
    model=None,             # str | None
    max_tokens=None,        # int | None
    temperature=None,       # float | None
    top_p=None,             # float | None
    top_k=None,             # int | None
    metadata=None,          # dict | None
    overwrite=False,        # bool
) -> Session
```

#### `get_session(session_id=None) -> Session`
#### `delete_session(session_id) -> None`
#### `clear_history(session_id=None) -> None`
#### `get_history(session_id=None) -> list[Message]`
#### `list_sessions() -> list[str]`
#### `set_session_system_prompt(system_prompt, session_id=None) -> None`
#### `get_token_usage(session_id=None) -> TokenUsage`
#### `get_all_token_usage() -> dict[str, TokenUsage]`

---

### Tools

---

#### `@box.tool` / `box.tool`

Decorator. Can be used as `@box.tool` or `@box.tool(name=..., description=..., timeout=...)`.

```python
@box.tool
def my_function(param: str) -> str: ...

@box.tool(name="my_tool", description="Does a thing", timeout=10.0)
def my_function(param: str) -> str: ...
```

#### `register_tool(fn, *, name=None, description=None, schema=None, timeout=None) -> None`
#### `unregister_tool(name) -> None`
#### `unregister_all_tools() -> None`
#### `list_tools() -> list[str]`

---

### Batches

---

#### `submit_batch(requests) -> BatchStatus`
#### `poll_batch(batch_id) -> BatchStatus`
#### `wait_for_batch(batch_id) -> BatchStatus`
#### `get_batch_results(batch_id) -> list[BatchResult]`

#### `run_batch()`

```python
box.run_batch(
    requests,   # list[BatchRequest]
) -> list[BatchResult]
```

Convenience: submits, waits, returns all results.

---

### Files

---

#### `upload_file()`

```python
box.upload_file(
    file,           # Path | (filename, bytes, mime_type) | BinaryIO
    *,
    media_type=None # str | None
) -> UploadedFile
```

#### `delete_file(file_id) -> None`

---

### Events

---

#### `on(event, handler) -> ClaudeBox`
#### `once(event, handler) -> ClaudeBox`
#### `off(event, handler) -> ClaudeBox`
#### `off_all(event=None) -> ClaudeBox`
#### `listeners(event) -> list[Callable]`
#### `event_names() -> list[str]`

Auto-generated shorthands for every event in `EventName`:

```python
box.on_token(handler)           # on("token", handler)
box.once_token(handler)         # once("token", handler)
box.off_token(handler)          # off("token", handler)
box.on_response(handler)
box.on_tool_call(handler)
box.on_tool_result(handler)
box.on_error(handler)
# ... one set for every EventName value
```

---

### Config

---

#### `config_snapshot() -> ConfigSnapshot`
#### `reload_config() -> None`
#### `config -> Config`  *(property)*

---

### Internal access

---

#### `sync_client -> anthropic.Anthropic`  *(property)*
#### `async_client -> anthropic.AsyncAnthropic`  *(property)*
#### `conversation -> ConversationManager`  *(property)*
#### `tools_registry -> ToolRegistry`  *(property)*

---

### Lifecycle

---

#### `close() -> None`

Closes HTTP connections and shuts down the event bus thread pool.

#### Context managers

```python
with ClaudeBox() as box: ...
async with ClaudeBox() as box: ...
```

---

## Data Types

---

### ClaudeResponse

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Unique message ID |
| `model` | `str` | Model used |
| `role` | `str` | Always `"assistant"` |
| `content` | `list[ContentBlock]` | All content blocks |
| `stop_reason` | `StopReason \| None` | Why generation stopped |
| `stop_sequence` | `str \| None` | Which stop sequence matched |
| `usage` | `TokenUsage` | Token counts |
| `request_id` | `str \| None` | Anthropic request ID |
| `raw` | `Any` | Original SDK response |
| `text` | `str` *(property)* | All text blocks joined |
| `thinking` | `str` *(property)* | All thinking blocks joined |
| `tool_calls` | `list[ToolCall]` *(property)* | Tool use blocks |
| `has_tool_calls` | `bool` *(property)* | |
| `has_thinking` | `bool` *(property)* | |

---

### TokenUsage

| Attribute | Type |
|---|---|
| `input_tokens` | `int` |
| `output_tokens` | `int` |
| `cache_creation_input_tokens` | `int` |
| `cache_read_input_tokens` | `int` |
| `total_tokens` | `int` *(property)* |

Supports `+` operator for accumulation.

---

### StreamToken

| Attribute | Type |
|---|---|
| `text` | `str` |
| `index` | `int` |

---

### StreamThinkingToken

| Attribute | Type |
|---|---|
| `thinking` | `str` |
| `index` | `int` |

---

### ToolCall

| Attribute | Type |
|---|---|
| `id` | `str` |
| `name` | `str` |
| `input` | `dict[str, Any]` |

---

### ToolResult

| Attribute | Type |
|---|---|
| `tool_use_id` | `str` |
| `tool_name` | `str` |
| `output` | `Any` |
| `is_error` | `bool` |
| `execution_time_ms` | `float \| None` |

---

### Session

| Attribute | Type |
|---|---|
| `id` | `str` |
| `history` | `list[Message]` |
| `system_prompt` | `str \| None` |
| `model` | `str \| None` |
| `max_tokens` | `int \| None` |
| `temperature` | `float \| None` |
| `top_p` | `float \| None` |
| `top_k` | `int \| None` |
| `metadata` | `dict` |
| `token_usage` | `SessionTokenUsage` |
| `created_at` | `float` |
| `updated_at` | `float` |
| `message_count` | `int` *(property)* |

---

### BatchRequest

```python
BatchRequest(
    custom_id,          # str — unique ID for this request
    content,            # str | list[ContentBlock]
    model=None,
    max_tokens=None,
    temperature=None,
    top_p=None,
    top_k=None,
    stop_sequences=None,
    system=None,
    tools=None,
    tool_choice=None,
    metadata=None,
    betas=None,
)
```

---

### BatchResult

| Attribute | Type |
|---|---|
| `custom_id` | `str` |
| `status` | `BatchRequestStatus` |
| `response` | `ClaudeResponse \| None` |
| `error` | `dict \| None` |

---

### BatchStatus

| Attribute | Type |
|---|---|
| `id` | `str` |
| `processing_status` | `BatchProcessingStatus` |
| `request_counts` | `dict[str, int]` |

---

### Content Blocks

#### `TextBlock(text, cache_control=None)`
#### `ImageBlock(source, cache_control=None)`
#### `ImageSource(type, media_type=None, data=None, url=None)`
#### `DocumentBlock(source, title=None, context=None, citations=None, cache_control=None)`
#### `DocumentSource(type, media_type=None, data=None, url=None, text=None, file_id=None)`
#### `ToolUseBlock(id, name, input)`
#### `ToolResultBlock(tool_use_id, content, is_error=False)`
#### `ThinkingBlock(thinking)`
#### `RedactedThinkingBlock(data)`

---

### Enums

#### `Role`
`USER = "user"` · `ASSISTANT = "assistant"`

#### `StopReason`
`END_TURN` · `MAX_TOKENS` · `STOP_SEQUENCE` · `TOOL_USE` · `PAUSE_TURN` · `REFUSAL`

#### `MediaType`
`JPEG` · `PNG` · `GIF` · `WEBP` · `PDF` · `PLAIN`

#### `BatchRequestStatus`
`SUCCEEDED` · `ERRORED` · `CANCELED` · `EXPIRED`

#### `BatchProcessingStatus`
`IN_PROGRESS` · `CANCELING` · `ENDED`

#### `EventName`
See [Events section in GUIDE.md](GUIDE.md#13-events--the-output-bus) for full catalogue.

---

## EventName Values

```python
from claudebox import EventName

EventName.BOX_INITIALIZED
EventName.BOX_CLOSED
EventName.REQUEST_START
EventName.REQUEST_END
EventName.RESPONSE
EventName.TEXT
EventName.TOKEN
EventName.THINKING_TOKEN
EventName.THINKING
EventName.STREAM_START
EventName.STREAM_END
EventName.STREAM_EVENT
EventName.STREAM_ERROR
EventName.TOOL_CALL
EventName.TOOL_RESULT
EventName.TOOL_ERROR
EventName.TOOL_REGISTERED
EventName.TOOL_UNREGISTERED
EventName.SESSION_CREATED
EventName.SESSION_CLEARED
EventName.SESSION_DELETED
EventName.HISTORY_TRUNCATED
EventName.TOKEN_USAGE
EventName.BATCH_CREATED
EventName.BATCH_COMPLETE
EventName.BATCH_RESULT
EventName.BATCH_POLL
EventName.FILE_UPLOADED
EventName.FILE_DELETED
EventName.CONFIG_LOADED
EventName.CONFIG_RELOADED
EventName.ERROR
EventName.API_ERROR
EventName.RATE_LIMIT
EventName.RAW_REQUEST
EventName.RAW_RESPONSE
```
