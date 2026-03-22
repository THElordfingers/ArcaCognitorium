# ClaudeBox User Guide

> **Version:** 0.1.0  
> **Requires:** Python 3.9+ · `pip install anthropic pyyaml`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Getting Started](#3-getting-started)
4. [The Control Panel (claudebox.config.yaml)](#4-the-control-panel)
5. [Sending Messages](#5-sending-messages)
6. [Streaming](#6-streaming)
7. [Multi-Turn Conversations & Sessions](#7-multi-turn-conversations--sessions)
8. [Tool Use](#8-tool-use)
9. [Vision & Image Input](#9-vision--image-input)
10. [File Uploads (Files API)](#10-file-uploads-files-api)
11. [Batch Processing](#11-batch-processing)
12. [Extended Thinking](#12-extended-thinking)
13. [Events — The Output Bus](#13-events--the-output-bus)
14. [Token Counting & Usage](#14-token-counting--usage)
15. [Async Usage](#15-async-usage)
16. [Threaded Usage (GUI Apps)](#16-threaded-usage-gui-apps)
17. [Error Handling](#17-error-handling)
18. [Advanced Usage](#18-advanced-usage)
19. [Platform Integrations (Bedrock / Vertex)](#19-platform-integrations)
20. [Configuration Reference](#20-configuration-reference)

---

## 1. Overview

ClaudeBox is a self-contained, modular Python client for the Anthropic Claude API. The design philosophy is simple:

- **Everything is inside.** Every API feature — streaming, tools, vision, batches, files, thinking — lives in the box.
- **Nothing is hidden.** Every internal component has a surface connector. Every config option is exposed in the control panel.
- **No opinions about the outside.** ClaudeBox doesn't care if it's running inside a CLI, a Tkinter window, a FastAPI server, or a test harness. Drop it in. Wire it up. Go.

### Package structure

```
claudebox/
├── __init__.py       # Public surface — import everything from here
├── client.py         # ClaudeBox class — the engine block
├── config.py         # Config loader and validator
├── events.py         # Event bus — all output ports
├── conversation.py   # Session and history management
├── streaming.py      # Unified streaming (sync/async/threaded/generator)
├── tools.py          # Tool registry and auto-run executor
├── models.py         # All typed input/output dataclasses
└── exceptions.py     # Complete exception hierarchy

claudebox.config.yaml # The control panel — every configurable option
```

---

## 2. Installation

Copy the `claudebox/` directory and `claudebox.config.yaml` into your project root, then install dependencies:

```bash
pip install anthropic pyyaml

# Optional extras
pip install keyring          # secure API key storage
pip install Pillow           # auto image resize (vision.auto_resize)
```

Set your API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or configure it in `claudebox.config.yaml` (see [Section 4](#4-the-control-panel)).

---

## 3. Getting Started

```python
from claudebox import ClaudeBox

# Initialize — auto-loads claudebox.config.yaml from current directory
box = ClaudeBox()

# Send a message
response = box.send("What is the capital of France?")
print(response.text)
# → "The capital of France is Paris."

# Access full response details
print(response.model)           # "claude-sonnet-4-6"
print(response.stop_reason)     # StopReason.END_TURN
print(response.usage.input_tokens)
print(response.usage.output_tokens)
```

### Explicit config path

```python
box = ClaudeBox("/path/to/my/claudebox.config.yaml")
```

### Init-time overrides

```python
box = ClaudeBox(
    api_key="sk-ant-...",
    model="claude-opus-4-6",
    system_prompt="You are a helpful assistant.",
    max_tokens=2048,
    stream=False,
)
```

### Context manager (auto-closes connections)

```python
with ClaudeBox() as box:
    response = box.send("Hello")
    print(response.text)
```

---

## 4. The Control Panel

`claudebox.config.yaml` is the single place where every configurable option is exposed. It ships with the package and lives at your project root.

Open it and read it top to bottom. Every option has an inline comment explaining what it does, what values are valid, and what the default is.

### Config priority (highest to lowest)

```
1. Per-request arguments  →  box.send("hello", model="claude-opus-4-6")
2. Per-session overrides  →  box.create_session("s1", model="claude-opus-4-6")
3. claudebox.config.yaml  →  model: claude-opus-4-6
4. Built-in defaults      →  last resort only
```

### Hot reload at runtime

```python
# Re-reads and re-validates claudebox.config.yaml without restarting
box.reload_config()
```

### Inspect current effective config

```python
snapshot = box.config_snapshot()
print(snapshot.model)
print(snapshot.stream)
print(snapshot.thinking_enabled)
print(snapshot.raw)          # full raw dict
```

### Direct config access

```python
# Full Config object
cfg = box.config

cfg.model.model              # "claude-sonnet-4-6"
cfg.connection.max_retries   # 2
cfg.tools.auto_run_tools     # True
cfg.beta.code_execution      # False

# As dict
cfg.model.as_dict()
cfg.raw                      # full deep copy
```

---

## 5. Sending Messages

`send()` is the primary input port. Every parameter is optional — config and session defaults fill in the gaps.

### Basic usage

```python
response = box.send("Explain quantum computing in simple terms.")
print(response.text)
```

### With parameters

```python
response = box.send(
    "Write a haiku about rain.",
    model="claude-haiku-4-5-20251001",
    max_tokens=100,
    temperature=0.9,
    top_p=None,
    top_k=None,
    stop_sequences=["###"],
    system="You are a poet. Respond only with poems.",
    stream=False,
    service_tier="auto",
)
```

### The response object

```python
response.id                  # unique message ID
response.model               # model used
response.text                # all text blocks joined as a string
response.content             # list of ContentBlock objects (TextBlock, ToolUseBlock, etc.)
response.stop_reason         # StopReason enum
response.stop_sequence        # which stop sequence triggered (if any)
response.usage.input_tokens
response.usage.output_tokens
response.usage.cache_read_input_tokens
response.usage.cache_creation_input_tokens
response.has_tool_calls      # bool
response.has_thinking        # bool
response.thinking            # thinking text (if extended thinking enabled)
response.tool_calls          # list of ToolCall objects
response.request_id          # for debugging with Anthropic support
response.raw                 # original anthropic SDK response object
```

### Rich content input

You can send text, images, documents, and tool results in a single message:

```python
from claudebox import TextBlock, ImageBlock, ImageSource

response = box.send([
    ImageBlock(source=ImageSource(type="url", url="https://example.com/chart.png")),
    TextBlock(text="What trend does this chart show?"),
])
```

---

## 6. Streaming

Streaming is enabled by default (`streaming.enabled: true` in config). When streaming is on, `send()` fires `on_token` events as tokens arrive and returns the complete `ClaudeResponse` when done.

### Event-based (recommended)

```python
box.on_token(lambda t: print(t.text, end="", flush=True))
response = box.send("Tell me a long story.")
print()  # newline after stream ends
```

### Generator style — sync

```python
for token in box.stream("Tell me a long story."):
    print(token, end="", flush=True)
print()
```

### Generator style — async

```python
async for token in box.stream_async("Tell me a long story."):
    print(token, end="", flush=True)
```

### Disable streaming for a single request

```python
response = box.send("Hello", stream=False)
```

### Disable streaming globally

In `claudebox.config.yaml`:
```yaml
streaming:
  enabled: false
```

### Raw SSE events

If you need access to every raw event from the API:

```yaml
streaming:
  yield_raw_events: true
```

```python
box.on_stream_event(lambda e: print(e.type, e.data))
```

---

## 7. Multi-Turn Conversations & Sessions

ClaudeBox automatically maintains conversation history. Every `send()` call adds the user message and assistant response to the active session. The full history is sent with each subsequent request.

### Default session

```python
box.send("My name is Alice.")
response = box.send("What is my name?")
print(response.text)  # "Your name is Alice."
```

### Named sessions

```python
# Two independent conversations running simultaneously
box.send("My name is Alice.", session_id="alice")
box.send("My name is Bob.", session_id="bob")

response_a = box.send("What is my name?", session_id="alice")
response_b = box.send("What is my name?", session_id="bob")

print(response_a.text)   # "Your name is Alice."
print(response_b.text)   # "Your name is Bob."
```

### Creating sessions with config overrides

```python
# This session always uses Opus, regardless of global config
box.create_session(
    "my_session",
    system_prompt="You are a concise assistant. Keep all answers under 50 words.",
    model="claude-opus-4-6",
    max_tokens=200,
    temperature=0.3,
)

box.send("Explain neural networks.", session_id="my_session")
```

### Session management

```python
box.list_sessions()                    # ["default", "alice", "bob"]
box.get_session("alice")               # Session object
box.clear_history("alice")             # wipe history, keep session
box.delete_session("alice")            # remove session entirely
box.set_session_system_prompt("You are a pirate.", session_id="bob")
```

### Reading history

```python
messages = box.get_history("alice")
for msg in messages:
    print(f"{msg.role}: {msg.content}")
```

### History limits

In `claudebox.config.yaml`:
```yaml
conversation:
  max_history_messages: 20       # keep last 20 messages
  truncation_strategy: "drop_oldest"   # or "error"
  auto_clear_after_turn: false   # wipe history after each turn (one-shot mode)
```

---

## 8. Tool Use

Register Python functions as tools. Claude will call them automatically when it decides to use them.

### Decorator registration

```python
import json

@box.tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: City and state, e.g. "London, UK"
    """
    # Your real implementation here
    return json.dumps({"location": location, "temperature": "18°C", "condition": "Cloudy"})

response = box.send("What's the weather like in London?")
print(response.text)
# Claude calls get_weather, gets the result, and answers naturally
```

ClaudeBox automatically extracts:
- **Name** from the function name
- **Description** from the docstring (first line)
- **Parameter schema** from type hints + Args docstring section

### Decorator with explicit options

```python
@box.tool(name="weather", description="Fetch current weather data", timeout=10.0)
def fetch_weather(location: str, units: str = "celsius") -> str:
    ...
```

### Explicit registration

```python
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for information.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
    """
    ...

box.register_tool(search_web)

# Or with overrides
box.register_tool(search_web, name="web_search", timeout=15.0)
```

### Async tools

```python
@box.tool
async def fetch_database(query: str) -> str:
    """Query the database asynchronously."""
    result = await db.execute(query)
    return json.dumps(result)
```

### Tool management

```python
box.list_tools()                    # ["get_weather", "search_web"]
box.unregister_tool("get_weather")
box.unregister_all_tools()
```

### Manual tool execution (auto_run_tools: false)

If you want to handle tool calls yourself instead of letting ClaudeBox execute them automatically, set `tools.auto_run_tools: false` in config. Then subscribe to the tool call event:

```python
# config: tools.auto_run_tools: false

def handle_tool_call(tool_call):
    print(f"Claude wants to call: {tool_call.name}")
    print(f"With input: {tool_call.input}")
    # Execute yourself and feed the result back manually

box.on_tool_call(handle_tool_call)
response = box.send("What's the weather?")
```

### Tool choice

Control which tools Claude must/can use:

```yaml
tools:
  tool_choice: "auto"    # Claude decides (default)
  tool_choice: "any"     # Claude must use at least one tool
  tool_choice: "none"    # Claude cannot use tools
  tool_choice: "get_weather"  # Claude must use this specific tool
```

Or per-request:

```python
response = box.send("What's the weather?", tool_choice="any")
```

---

## 9. Vision & Image Input

Claude can analyze images passed as base64-encoded data or via URL.

### From a URL

```python
from claudebox import ImageBlock, ImageSource, TextBlock

response = box.send([
    ImageBlock(source=ImageSource(type="url", url="https://example.com/image.jpg")),
    TextBlock(text="Describe what you see in this image."),
])
print(response.text)
```

### From a local file

```python
import base64
from pathlib import Path
from claudebox import ImageBlock, ImageSource, TextBlock

image_data = base64.standard_b64encode(Path("photo.png").read_bytes()).decode()

response = box.send([
    ImageBlock(source=ImageSource(
        type="base64",
        media_type="image/png",
        data=image_data,
    )),
    TextBlock(text="What is in this image?"),
])
```

### Supported media types

- `image/jpeg`
- `image/png`
- `image/gif`
- `image/webp`

### Multiple images

```python
response = box.send([
    ImageBlock(source=ImageSource(type="url", url="https://example.com/before.jpg")),
    TextBlock(text="Before:"),
    ImageBlock(source=ImageSource(type="url", url="https://example.com/after.jpg")),
    TextBlock(text="After:"),
    TextBlock(text="What changed between these two images?"),
])
```

---

## 10. File Uploads (Files API)

The Files API lets you upload a file once and reference it in multiple requests by ID.

Enable it in `claudebox.config.yaml`:

```yaml
files:
  enabled: true
  beta_header: "files-api-2025-04-14"
```

### Upload a file

```python
from pathlib import Path

uploaded = box.upload_file(Path("report.pdf"))
print(uploaded.file_id)   # "file_abc123"
```

### Reference in a message

```python
from claudebox import DocumentBlock, DocumentSource, TextBlock

response = box.send([
    DocumentBlock(source=DocumentSource(type="file", file_id=uploaded.file_id)),
    TextBlock(text="Summarize the key findings in this report."),
])
```

### Delete a file

```python
box.delete_file(uploaded.file_id)
```

---

## 11. Batch Processing

Submit many requests at once for async processing. More cost-effective for bulk workloads.

### Submit and wait for results

```python
from claudebox import BatchRequest

requests = [
    BatchRequest(custom_id="q1", content="Summarize: The quick brown fox..."),
    BatchRequest(custom_id="q2", content="Translate to French: Hello world"),
    BatchRequest(custom_id="q3", content="Explain recursion in one sentence."),
]

# Submits, polls until done, returns all results
results = box.run_batch(requests)

for result in results:
    print(f"{result.custom_id}: {result.status}")
    if result.response:
        print(f"  → {result.response.text}")
```

### Submit and poll manually

```python
status = box.submit_batch(requests)
print(f"Batch ID: {status.id}")

# Poll yourself
while True:
    status = box.poll_batch(status.id)
    print(f"Status: {status.processing_status}")
    if status.processing_status.value == "ended":
        break
    time.sleep(60)

results = box.get_batch_results(status.id)
```

### Per-request config

```python
BatchRequest(
    custom_id="analysis",
    content="Analyze this financial data...",
    model="claude-opus-4-6",
    max_tokens=4096,
    temperature=0.0,
    system="You are a financial analyst.",
)
```

### Batch config

```yaml
batches:
  poll_interval_seconds: 60
  auto_poll: true
  max_poll_wait_seconds: 3600    # 1 hour max wait
  raise_on_partial_failure: false
```

---

## 12. Extended Thinking

Extended thinking lets Claude reason internally before responding, improving accuracy on complex tasks.

Enable in `claudebox.config.yaml`:

```yaml
thinking:
  enabled: true
  budget_tokens: 10000    # tokens Claude can use for reasoning (min 1024)
  stream_thinking: true   # fire on_thinking_token events while thinking
```

Or per-request:

```python
response = box.send(
    "Solve this step by step: If a train leaves Chicago at 9am...",
    thinking_enabled=True,
    thinking_budget_tokens=8000,
)

print(response.thinking)   # Claude's internal reasoning
print(response.text)       # Claude's final answer
```

### Streaming thinking tokens

```python
box.on_thinking_token(lambda t: print(f"[thinking] {t.thinking}", end=""))
box.on_token(lambda t: print(t.text, end="", flush=True))
response = box.send("What is 17 * 23 * 41?", thinking_enabled=True)
```

---

## 13. Events — The Output Bus

Every significant event that happens inside ClaudeBox fires an event on the bus. Subscribe to any combination of events from outside the box.

### Subscribing

```python
# Subscribe
box.on("token", my_handler)

# Shorthand (auto-generated for every event)
box.on_token(my_handler)
box.on_response(my_handler)
box.on_tool_call(my_handler)

# Fire once then auto-unsubscribe
box.once("response", my_handler)
box.once_response(my_handler)

# Unsubscribe
box.off("token", my_handler)
box.off_token(my_handler)

# Remove all handlers for an event
box.off_all("token")

# Remove all handlers for all events
box.off_all()

# Inspect
box.listeners("token")     # list of handlers
box.event_names()          # all events with at least one subscriber
```

### Complete event catalogue

| Event | Shorthand | Payload | Description |
|---|---|---|---|
| `box_initialized` | `on_box_initialized` | `ClaudeBox` | Box fully initialized |
| `box_closed` | `on_box_closed` | `ClaudeBox` | Box closed |
| `request_start` | `on_request_start` | `dict` | About to send a request |
| `request_end` | `on_request_end` | `dict` | Request complete |
| `response` | `on_response` | `ClaudeResponse` | Full response received |
| `text` | `on_text` | `str` | Complete response text |
| `token` | `on_token` | `StreamToken` | Single streaming token |
| `thinking_token` | `on_thinking_token` | `StreamThinkingToken` | Thinking token |
| `thinking` | `on_thinking` | `str` | Complete thinking text |
| `stream_start` | `on_stream_start` | `None` | Stream opened |
| `stream_end` | `on_stream_end` | `StreamComplete` | Stream closed |
| `stream_event` | `on_stream_event` | `StreamEvent` | Raw SSE event |
| `stream_error` | `on_stream_error` | `Exception` | Error during stream |
| `tool_call` | `on_tool_call` | `ToolCall` | Claude calling a tool |
| `tool_result` | `on_tool_result` | `ToolResult` | Tool execution result |
| `tool_error` | `on_tool_error` | `dict` | Tool execution failed |
| `tool_registered` | `on_tool_registered` | `str` (name) | Tool registered |
| `tool_unregistered` | `on_tool_unregistered` | `str` (name) | Tool unregistered |
| `session_created` | `on_session_created` | `Session` | New session |
| `session_cleared` | `on_session_cleared` | `str` (id) | History cleared |
| `session_deleted` | `on_session_deleted` | `str` (id) | Session deleted |
| `history_truncated` | `on_history_truncated` | `dict` | History truncated |
| `token_usage` | `on_token_usage` | `TokenUsage` | Usage after request |
| `batch_created` | `on_batch_created` | `BatchStatus` | Batch submitted |
| `batch_complete` | `on_batch_complete` | `BatchStatus` | Batch done |
| `batch_result` | `on_batch_result` | `BatchResult` | Single batch result |
| `batch_poll` | `on_batch_poll` | `BatchStatus` | Batch poll tick |
| `file_uploaded` | `on_file_uploaded` | `UploadedFile` | File uploaded |
| `file_deleted` | `on_file_deleted` | `str` (id) | File deleted |
| `config_loaded` | `on_config_loaded` | `Config` | Config loaded |
| `config_reloaded` | `on_config_reloaded` | `Config` | Config hot-reloaded |
| `error` | `on_error` | `Exception` | Any error (catch-all) |
| `api_error` | `on_api_error` | `APIError` | API-specific error |
| `rate_limit` | `on_rate_limit` | `RateLimitError` | Rate limit hit |
| `raw_request` | `on_raw_request` | `dict` | Raw API request params |
| `raw_response` | `on_raw_response` | `object` | Raw SDK response |

### StreamToken payload

```python
def on_token(token):
    token.text     # the text string (e.g. "Hello")
    token.index    # content block index

box.on_token(on_token)
```

### Async handlers

Handlers can be sync or async — ClaudeBox detects and handles both:

```python
async def my_async_handler(response):
    await save_to_database(response.text)

box.on_response(my_async_handler)
```

### Event bus config

```yaml
events:
  enabled: true
  async_handlers: false          # true = dispatch handlers in thread pool
  handler_thread_pool_size: 4
  suppress_handler_errors: true  # false = raise EventHandlerError
  allow_unknown_events: false    # true = allow custom event names
```

---

## 14. Token Counting & Usage

### Count before sending (no API call made)

```python
token_count = box.count_tokens(
    "Explain the theory of relativity.",
    system="You are a physics professor.",
)
print(f"This request will use approximately {token_count} input tokens")
```

### Usage after a request

```python
response = box.send("Hello")
print(response.usage.input_tokens)
print(response.usage.output_tokens)
print(response.usage.total_tokens)
print(response.usage.cache_read_input_tokens)
print(response.usage.cache_creation_input_tokens)
```

### Cumulative session usage

```python
# Total tokens used in the default session so far
usage = box.get_token_usage()
print(usage.input_tokens)
print(usage.output_tokens)
print(usage.total_tokens)

# Named session
usage = box.get_token_usage("alice")

# All sessions
all_usage = box.get_all_token_usage()
for session_id, usage in all_usage.items():
    print(f"{session_id}: {usage.total_tokens} total tokens")
```

### Usage event

```python
box.on_token_usage(lambda u: print(f"Used: {u.input_tokens} in / {u.output_tokens} out"))
```

---

## 15. Async Usage

ClaudeBox has a full async API alongside the sync one. Use `send_async()` and `stream_async()` in any asyncio context.

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    box = ClaudeBox()

    # Simple async send
    response = await box.send_async("Hello, Claude")
    print(response.text)

    # Async streaming via generator
    async for token in box.stream_async("Tell me a story"):
        print(token, end="", flush=True)

    # Async context manager
    async with ClaudeBox() as box:
        response = await box.send_async("Hello")
        print(response.text)

asyncio.run(main())
```

### Async event handlers

```python
async def save_response(response):
    await database.insert(response.text)

box.on_response(save_response)  # async handlers work automatically
response = await box.send_async("Write a report.")
```

### Concurrent sessions

```python
async def chat(session_id: str, message: str):
    return await box.send_async(message, session_id=session_id)

# Run multiple sessions concurrently
results = await asyncio.gather(
    chat("alice", "What's your favourite colour?"),
    chat("bob", "What's your favourite food?"),
    chat("carol", "What's your favourite season?"),
)
```

---

## 16. Threaded Usage (GUI Apps)

For GUI frameworks (Tkinter, PyQt, wx) that have their own event loop, use `send_threaded()` to run requests in a background thread without blocking the UI.

### Tkinter example

```python
import tkinter as tk
from tkinter import scrolledtext
from claudebox import ClaudeBox

box = ClaudeBox()

def send_message():
    user_text = entry.get().strip()
    if not user_text:
        return
    entry.delete(0, tk.END)
    chat.insert(tk.END, f"You: {user_text}\n")

    def on_token(token):
        # Schedule UI update on main thread
        chat.after(0, lambda t=token.text: chat.insert(tk.END, t))

    def on_complete(response):
        chat.after(0, lambda: chat.insert(tk.END, "\n\n"))

    def on_error(err):
        chat.after(0, lambda: chat.insert(tk.END, f"\n[Error: {err}]\n\n"))

    chat.insert(tk.END, "Claude: ")
    box.send_threaded(
        user_text,
        on_token=on_token,
        on_complete=on_complete,
        on_error=on_error,
    )

root = tk.Tk()
root.title("Claude Chat")
chat = scrolledtext.ScrolledText(root, wrap=tk.WORD)
chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
frame = tk.Frame(root)
frame.pack(fill=tk.X, padx=10, pady=5)
entry = tk.Entry(frame, font=("Arial", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", lambda e: send_message())
tk.Button(frame, text="Send", command=send_message).pack(side=tk.RIGHT)
root.mainloop()
```

### PyQt6 example

```python
from PyQt6.QtCore import QThread, pyqtSignal

class SendWorker(QThread):
    token_received = pyqtSignal(str)
    complete = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, box, content, session_id=None):
        super().__init__()
        self.box = box
        self.content = content
        self.session_id = session_id

    def run(self):
        try:
            def on_token(t):
                self.token_received.emit(t.text)
            response = self.box.send(
                self.content,
                session_id=self.session_id,
            )
            self.complete.emit(response)
        except Exception as e:
            self.error.emit(str(e))

# Usage
worker = SendWorker(box, "Hello Claude")
worker.token_received.connect(lambda t: text_widget.insertPlainText(t))
worker.complete.connect(lambda r: print("Done:", r.text))
worker.start()
```

### Streaming thread mode config

```yaml
streaming:
  thread_mode: "threaded"    # runs stream in background thread automatically
```

---

## 17. Error Handling

Every error in ClaudeBox has its own exception type. All are importable from `claudebox` directly.

### Basic error handling

```python
from claudebox import (
    ClaudeBox,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    ToolExecutionError,
    SessionNotFoundError,
)

box = ClaudeBox()

try:
    response = box.send("Hello")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except APIConnectionError as e:
    print(f"Network error: {e.cause}")
except APITimeoutError:
    print("Request timed out")
except ClaudeBoxError as e:
    # Catch-all for any ClaudeBox error
    print(f"Error: {e.message}")
    if e.cause:
        print(f"Caused by: {e.cause}")
```

### Error event bus

```python
box.on_error(lambda e: logger.error(f"ClaudeBox error: {e}"))
box.on_api_error(lambda e: alert_ops_team(e))
box.on_rate_limit(lambda e: time.sleep(e.retry_after or 60))
```

### Full exception hierarchy

```
ClaudeBoxError
├── ConfigError
│   ├── ConfigNotFoundError
│   ├── ConfigParseError
│   └── ConfigValidationError
├── ClientError
│   ├── AuthenticationError
│   └── ClientNotInitializedError
├── APIError
│   ├── APIConnectionError
│   ├── APITimeoutError
│   ├── RateLimitError          — has .retry_after
│   ├── BadRequestError         — HTTP 400
│   ├── APIAuthorizationError   — HTTP 401
│   ├── PermissionDeniedError   — HTTP 403
│   ├── APINotFoundError        — HTTP 404
│   ├── UnprocessableEntityError — HTTP 422
│   ├── InternalServerError     — HTTP 5xx
│   └── OverloadedError         — HTTP 529
├── ConversationError
│   ├── SessionNotFoundError    — has .session_id
│   ├── SessionAlreadyExistsError
│   ├── HistoryTruncationError
│   └── InvalidMessageRoleError
├── StreamingError
│   ├── StreamNotStartedError
│   ├── StreamAlreadyConsumedError
│   └── StreamInterruptedError  — has .partial_text
├── ToolError
│   ├── ToolNotFoundError       — has .tool_name
│   ├── ToolAlreadyRegisteredError
│   ├── ToolExecutionError
│   ├── ToolValidationError     — has .validation_errors
│   ├── ToolTimeoutError        — has .timeout
│   └── MaxToolIterationsError  — has .iterations
├── VisionError
│   ├── UnsupportedMediaTypeError
│   ├── ImageTooLargeError      — has .size_bytes, .max_bytes
│   └── ImageLoadError
├── FileError
│   ├── FileUploadError
│   ├── FilesAPINotFoundError
│   └── FileAPINotEnabledError
├── BatchError
│   ├── BatchCreationError
│   ├── BatchPollError          — has .batch_id
│   └── BatchResultError
├── EventError
│   ├── EventHandlerError       — has .event_name
│   └── UnknownEventError
└── ThinkingError
    └── ThinkingBudgetError     — has .budget_tokens
```

All exceptions carry `.message`, `.cause` (original exception), and `.context` (optional dict).

---

## 18. Advanced Usage

### Direct access to internal components

For cases where you need to reach past the surface:

```python
# Raw Anthropic SDK clients
box.sync_client      # anthropic.Anthropic instance
box.async_client     # anthropic.AsyncAnthropic instance

# Internal components
box.config           # Config object
box.conversation     # ConversationManager
box.tools_registry   # ToolRegistry
```

### Escape hatch — raw API kwargs

Pass any parameter directly to the Anthropic API that ClaudeBox doesn't have a named argument for:

```python
response = box.send(
    "Hello",
    **{"some_future_param": "value"}
)
```

### Custom event names

```yaml
events:
  allow_unknown_events: true
```

```python
box._bus.on("my_custom_event", handler)
box._bus.emit("my_custom_event", {"data": "anything"})
```

### Prompt caching

```yaml
cache:
  enabled: true
  auto_cache_system_prompt: true
  auto_cache_history: true
  auto_cache_history_n: 2

system:
  cache_control: true
  cache_control_type: "ephemeral"
```

### Beta features

Enable any beta feature in config:

```yaml
beta:
  code_execution: true
  extended_output: true
  computer_use: false
```

Or per-request:

```python
response = box.send(
    "Run this Python code: print(1+1)",
    betas=["code-execution-2025-05-22"],
)
```

### Logging

```yaml
logging:
  level: "debug"               # see everything
  log_requests: true           # log outgoing request params
  log_responses: true          # log raw responses
  log_token_usage: true
  log_tool_calls: true
  log_to_file: true
  log_file_path: "claudebox.log"
  log_file_max_bytes: 10485760
  log_file_backup_count: 3
```

### Secure API key storage

```bash
pip install keyring
```

```yaml
api:
  api_key_source: "keyring"

keyring:
  service_name: "my_app"
  username: "anthropic_api_key"
```

```python
import keyring
keyring.set_password("my_app", "anthropic_api_key", "sk-ant-...")
```

### Retries and timeouts

```yaml
connection:
  max_retries: 3
  timeout_total: 300.0
  timeout_connect: 5.0
  timeout_read: 120.0
  timeout_write: 30.0
```

Per-request (via escape hatch):

```python
response = box.sync_client.with_options(
    timeout=10.0,
    max_retries=0,
).messages.create(...)
```

---

## 19. Platform Integrations

### AWS Bedrock

```yaml
platform:
  provider: "bedrock"
  bedrock:
    aws_region: "us-east-1"
    aws_access_key: null      # or set explicitly
    aws_secret_key: null      # or use IAM role / env vars
    aws_session_token: null
    aws_profile: "my-profile"
```

Install extra:
```bash
pip install anthropic[bedrock]
```

### Google Vertex AI

```yaml
platform:
  provider: "vertex"
  vertex:
    project_id: "my-gcp-project"
    region: "us-east5"
    credentials: null    # null = use Application Default Credentials
```

Install extra:
```bash
pip install anthropic[vertex]
```

### HTTP proxy

```yaml
connection:
  proxy: "http://proxy.example.com:8080"
```

---

## 20. Configuration Reference

All 18 sections of `claudebox.config.yaml` with their default values:

### `api`
| Option | Default | Description |
|---|---|---|
| `api_key` | `null` | API key value (prefer null + env var) |
| `api_key_source` | `"env"` | `"env"` or `"keyring"` |
| `api_key_env_var` | `"ANTHROPIC_API_KEY"` | Env var name |
| `auth_token` | `null` | Alternative to api_key |
| `base_url` | `null` | Override API endpoint |
| `anthropic_version` | `"2023-06-01"` | API version header |
| `default_headers` | `{}` | Extra headers on every request |
| `default_query` | `{}` | Extra query params on every request |
| `strict_response_validation` | `false` | Raise on unknown API fields |

### `connection`
| Option | Default | Description |
|---|---|---|
| `timeout_total` | `600.0` | Total request timeout (seconds) |
| `timeout_connect` | `10.0` | Connection timeout |
| `timeout_read` | `300.0` | Read timeout |
| `timeout_write` | `30.0` | Write timeout |
| `max_retries` | `2` | Auto-retry attempts |
| `proxy` | `null` | HTTP proxy URL |
| `follow_redirects` | `true` | Follow HTTP redirects |
| `max_connections` | `100` | Connection pool size |
| `max_keepalive_connections` | `20` | Keepalive pool size |
| `keepalive_expiry` | `5.0` | Keepalive expiry (seconds) |
| `local_address` | `null` | Local bind address |

### `model`
| Option | Default | Description |
|---|---|---|
| `model` | `"claude-sonnet-4-6"` | Default model |
| `max_tokens` | `1024` | Max response tokens |
| `temperature` | `null` | 0.0–1.0, null = API default |
| `top_p` | `null` | Nucleus sampling, null = API default |
| `top_k` | `null` | Top-k sampling, null = disabled |
| `stop_sequences` | `[]` | Custom stop strings |
| `service_tier` | `null` | `null`, `"auto"`, or `"standard_only"` |

### `system`
| Option | Default | Description |
|---|---|---|
| `prompt` | `null` | Default system prompt |
| `cache_control` | `false` | Cache the system prompt |
| `cache_control_type` | `"ephemeral"` | Cache type (currently only ephemeral) |

### `thinking`
| Option | Default | Description |
|---|---|---|
| `enabled` | `false` | Enable extended thinking |
| `budget_tokens` | `5000` | Max thinking tokens (min 1024) |
| `stream_thinking` | `true` | Fire thinking token events |

### `conversation`
| Option | Default | Description |
|---|---|---|
| `multi_session` | `true` | Support named sessions |
| `default_session_id` | `"default"` | Default session name |
| `max_history_messages` | `null` | History limit (null = unlimited) |
| `truncation_strategy` | `"drop_oldest"` | `"drop_oldest"` or `"error"` |
| `auto_clear_after_turn` | `false` | Clear history after each exchange |
| `prefill` | `null` | Assistant turn prefill text |
| `include_prefill_in_response` | `true` | Include prefill in response text |

### `streaming`
| Option | Default | Description |
|---|---|---|
| `enabled` | `true` | Stream by default |
| `use_stream_helpers` | `true` | Use SDK stream helper |
| `yield_raw_events` | `false` | Emit raw SSE events |
| `thread_mode` | `"direct"` | `"direct"` or `"threaded"` |

### `tools`
| Option | Default | Description |
|---|---|---|
| `tool_choice` | `"auto"` | `"auto"`, `"any"`, `"none"`, or tool name |
| `auto_run_tools` | `true` | Auto-execute tools and loop |
| `max_tool_iterations` | `10` | Max tool loop iterations |
| `default_tool_timeout` | `30.0` | Per-tool timeout (seconds) |
| `validate_tool_inputs` | `true` | Validate inputs before execution |
| `include_tool_blocks_in_response` | `true` | Include ToolUseBlock in response.content |
| `include_tool_results_in_history` | `true` | Include tool results in history |

### `vision`
| Option | Default | Description |
|---|---|---|
| `default_media_type` | `"image/jpeg"` | Fallback media type for raw bytes |
| `max_image_size_bytes` | `5242880` | Max image size (5MB) |
| `auto_resize` | `false` | Auto-resize oversized images (requires Pillow) |
| `auto_resize_target_bytes` | `4000000` | Target size for auto-resize |
| `auto_encode_from_path` | `true` | Auto base64-encode from file path |

### `files`
| Option | Default | Description |
|---|---|---|
| `enabled` | `false` | Enable Files API |
| `beta_header` | `"files-api-2025-04-14"` | Beta header string |
| `default_upload_media_type` | `"application/octet-stream"` | Default MIME type |
| `cache_uploads` | `false` | Cache file IDs locally |
| `max_upload_size_bytes` | `null` | Max upload size |

### `batches`
| Option | Default | Description |
|---|---|---|
| `poll_interval_seconds` | `60` | Polling frequency |
| `auto_poll` | `true` | Auto-poll in `run_batch()` |
| `max_poll_wait_seconds` | `null` | Max wait time (null = indefinite) |
| `stream_results` | `true` | Stream results vs collect all |
| `raise_on_partial_failure` | `false` | Raise if any request fails |

### `events`
| Option | Default | Description |
|---|---|---|
| `enabled` | `true` | Enable event bus |
| `async_handlers` | `false` | Dispatch handlers in thread pool |
| `handler_thread_pool_size` | `4` | Thread pool size |
| `suppress_handler_errors` | `true` | Log vs raise handler errors |
| `allow_unknown_events` | `false` | Allow custom event names |

### `cache`
| Option | Default | Description |
|---|---|---|
| `enabled` | `false` | Enable prompt caching |
| `auto_cache_system_prompt` | `false` | Auto-cache system prompt |
| `auto_cache_history` | `false` | Auto-cache history messages |
| `auto_cache_history_n` | `2` | Number of history messages to cache |

### `beta`
Each beta feature has an `enabled` bool and a `_header` string. Set `enabled: true` to include that feature's header in every request.

| Feature | Header |
|---|---|
| `interleaved_thinking` | `interleaved-thinking-2025-05-14` |
| `code_execution` | `code-execution-2025-05-22` |
| `files_api` | `files-api-2025-04-14` |
| `mcp_connector` | `mcp-client-2025-04-04` |
| `extended_output` | `output-128k-2025-02-19` |
| `computer_use` | `computer-use-2025-01-24` |
| `token_counting` | `token-counting-2024-11-01` |
| `prompt_caching` | `prompt-caching-2024-07-31` |
| `message_batches` | `message-batches-2024-09-24` |
| `fine_tuning` | `fine-tuning-2024-11-15` |

Add arbitrary headers:
```yaml
beta:
  extra_beta_headers: ["my-feature-2025-01-01"]
```

### `metadata`
| Option | Default | Description |
|---|---|---|
| `user_id` | `null` | Opaque user ID for abuse detection |
| `extra` | `{}` | Additional metadata fields |

### `logging`
| Option | Default | Description |
|---|---|---|
| `level` | `"warning"` | `debug`, `info`, `warning`, `error`, `critical`, `off` |
| `sdk_log_level` | `"off"` | Anthropic SDK log level |
| `logger_name` | `"claudebox"` | Logger name |
| `log_requests` | `false` | Log outgoing request params |
| `log_responses` | `false` | Log raw API responses |
| `log_token_usage` | `true` | Log token usage per request |
| `log_tool_calls` | `true` | Log tool calls and results |
| `log_events` | `false` | Log event emissions |
| `log_to_file` | `false` | Write to log file |
| `log_file_path` | `"claudebox.log"` | Log file path |
| `log_file_max_bytes` | `10485760` | Rotation size (10MB) |
| `log_file_backup_count` | `3` | Backup file count |
| `log_format` | `"%(asctime)s ..."` | Python logging format string |
| `log_request_id` | `true` | Include request ID in logs |

### `platform`
| Option | Default | Description |
|---|---|---|
| `provider` | `"anthropic"` | `"anthropic"`, `"bedrock"`, or `"vertex"` |
| `bedrock.aws_region` | `null` | AWS region |
| `bedrock.aws_access_key` | `null` | AWS access key |
| `bedrock.aws_secret_key` | `null` | AWS secret key |
| `bedrock.aws_session_token` | `null` | AWS session token |
| `bedrock.aws_profile` | `null` | AWS profile name |
| `vertex.project_id` | `null` | GCP project ID |
| `vertex.region` | `"us-east5"` | GCP region |
| `vertex.credentials` | `null` | Path to service account JSON |

---

*ClaudeBox v0.1.0 — every feature, every input, every output.*
