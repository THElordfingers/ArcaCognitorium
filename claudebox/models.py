"""
claudebox.models
================
All data structures used as inputs and outputs across ClaudeBox.

Every piece of data that flows in or out of the box — messages, responses,
token counts, tool calls, tool results, stream events, batch results, file
references, thinking blocks, usage stats — is represented as a typed dataclass
or enum here. Nothing is left as a raw dict.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class StopReason(str, Enum):
    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"
    TOOL_USE = "tool_use"
    PAUSE_TURN = "pause_turn"
    REFUSAL = "refusal"


class ToolChoice(str, Enum):
    AUTO = "auto"
    ANY = "any"
    NONE = "none"
    # TOOL = specific tool name — handled separately as ToolChoiceSpecific


class MediaType(str, Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    WEBP = "image/webp"
    PDF = "application/pdf"
    PLAIN = "text/plain"


class ContentBlockType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    DOCUMENT = "document"
    THINKING = "thinking"
    REDACTED_THINKING = "redacted_thinking"


class StreamEventType(str, Enum):
    MESSAGE_START = "message_start"
    CONTENT_BLOCK_START = "content_block_start"
    CONTENT_BLOCK_DELTA = "content_block_delta"
    CONTENT_BLOCK_STOP = "content_block_stop"
    MESSAGE_DELTA = "message_delta"
    MESSAGE_STOP = "message_stop"
    PING = "ping"
    ERROR = "error"


class BatchRequestStatus(str, Enum):
    SUCCEEDED = "succeeded"
    ERRORED = "errored"
    CANCELED = "canceled"
    EXPIRED = "expired"


class BatchProcessingStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    CANCELING = "canceling"
    ENDED = "ended"


# ---------------------------------------------------------------------------
# Content blocks
# ---------------------------------------------------------------------------

@dataclass
class TextBlock:
    """A plain text content block."""
    text: str
    type: str = "text"
    cache_control: Optional[dict[str, str]] = None


@dataclass
class ImageSource:
    """Source for an image — either base64 or URL."""
    type: str                           # "base64" or "url"
    media_type: Optional[str] = None    # required for base64
    data: Optional[str] = None          # base64 encoded data
    url: Optional[str] = None           # for url type


@dataclass
class ImageBlock:
    """An image content block."""
    source: ImageSource
    type: str = "image"
    cache_control: Optional[dict[str, str]] = None


@dataclass
class DocumentSource:
    """Source for a document block."""
    type: str                           # "base64", "url", "text", or "file"
    media_type: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    file_id: Optional[str] = None


@dataclass
class DocumentBlock:
    """A document content block (PDF, text, etc.)."""
    source: DocumentSource
    type: str = "document"
    title: Optional[str] = None
    context: Optional[str] = None
    citations: Optional[dict] = None
    cache_control: Optional[dict[str, str]] = None


@dataclass
class ToolUseBlock:
    """Claude is requesting to use a tool."""
    id: str
    name: str
    input: dict[str, Any]
    type: str = "tool_use"


@dataclass
class ToolResultBlock:
    """Result of a tool execution to be sent back to Claude."""
    tool_use_id: str
    content: Union[str, list[Union[TextBlock, ImageBlock]]]
    type: str = "tool_result"
    is_error: bool = False


@dataclass
class ThinkingBlock:
    """Extended thinking block — Claude's internal reasoning."""
    thinking: str
    type: str = "thinking"


@dataclass
class RedactedThinkingBlock:
    """Redacted thinking block — thinking that has been redacted for safety."""
    data: str
    type: str = "redacted_thinking"


# Union of all valid content block types
ContentBlock = Union[
    TextBlock,
    ImageBlock,
    DocumentBlock,
    ToolUseBlock,
    ToolResultBlock,
    ThinkingBlock,
    RedactedThinkingBlock,
]


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """A single message in a conversation."""
    role: Union[Role, str]
    content: Union[str, list[ContentBlock]]

    def to_api_dict(self) -> dict:
        """Serialize to Anthropic API format."""
        role = self.role.value if isinstance(self.role, Role) else self.role
        if isinstance(self.content, str):
            return {"role": role, "content": self.content}
        return {"role": role, "content": [_serialize_block(b) for b in self.content]}


def _serialize_block(block: ContentBlock) -> dict:
    """Convert a content block dataclass to API dict format."""
    if isinstance(block, TextBlock):
        d: dict = {"type": "text", "text": block.text}
        if block.cache_control:
            d["cache_control"] = block.cache_control
        return d
    if isinstance(block, ImageBlock):
        src = {"type": block.source.type}
        if block.source.media_type:
            src["media_type"] = block.source.media_type
        if block.source.data:
            src["data"] = block.source.data
        if block.source.url:
            src["url"] = block.source.url
        d = {"type": "image", "source": src}
        if block.cache_control:
            d["cache_control"] = block.cache_control
        return d
    if isinstance(block, DocumentBlock):
        src: dict = {"type": block.source.type}
        for attr in ("media_type", "data", "url", "text", "file_id"):
            val = getattr(block.source, attr, None)
            if val is not None:
                src[attr] = val
        d = {"type": "document", "source": src}
        for attr in ("title", "context", "citations", "cache_control"):
            val = getattr(block, attr, None)
            if val is not None:
                d[attr] = val
        return d
    if isinstance(block, ToolUseBlock):
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    if isinstance(block, ToolResultBlock):
        d = {"type": "tool_result", "tool_use_id": block.tool_use_id, "is_error": block.is_error}
        if isinstance(block.content, str):
            d["content"] = block.content
        else:
            d["content"] = [_serialize_block(b) for b in block.content]
        return d
    if isinstance(block, ThinkingBlock):
        return {"type": "thinking", "thinking": block.thinking}
    if isinstance(block, RedactedThinkingBlock):
        return {"type": "redacted_thinking", "data": block.data}
    # Fallback — pass through raw dicts if somehow one sneaks in
    if isinstance(block, dict):
        return block
    raise ValueError(f"Unknown content block type: {type(block)}")


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@dataclass
class ToolParameter:
    """A single parameter in a tool's input schema."""
    name: str
    type: str
    description: Optional[str] = None
    enum: Optional[list[Any]] = None
    required: bool = True


@dataclass
class ToolDefinition:
    """
    Full definition of a tool as sent to the API.
    Includes the original Python callable for execution.
    """
    name: str
    description: str
    input_schema: dict[str, Any]
    callable: Optional[Any] = None          # The actual Python function
    is_async: bool = False
    timeout: Optional[float] = None         # Per-tool timeout in seconds

    def to_api_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolCall:
    """A tool call made by Claude — pre-execution."""
    id: str
    name: str
    input: dict[str, Any]


@dataclass
class ToolResult:
    """The result of executing a tool."""
    tool_use_id: str
    tool_name: str
    output: Any
    is_error: bool = False
    execution_time_ms: Optional[float] = None


# ---------------------------------------------------------------------------
# Token usage
# ---------------------------------------------------------------------------

@dataclass
class TokenUsage:
    """Token usage for a single API call."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_creation_input_tokens=self.cache_creation_input_tokens + other.cache_creation_input_tokens,
            cache_read_input_tokens=self.cache_read_input_tokens + other.cache_read_input_tokens,
        )


@dataclass
class SessionTokenUsage:
    """Cumulative token usage across an entire session."""
    total: TokenUsage = field(default_factory=TokenUsage)
    per_turn: list[TokenUsage] = field(default_factory=list)

    def record(self, usage: TokenUsage) -> None:
        self.per_turn.append(usage)
        self.total = self.total + usage


# ---------------------------------------------------------------------------
# API response
# ---------------------------------------------------------------------------

@dataclass
class ClaudeResponse:
    """
    Normalized response from a Claude API call.
    Wraps the raw API response and exposes all fields.
    """
    id: str
    model: str
    role: str
    content: list[ContentBlock]
    stop_reason: Optional[StopReason]
    stop_sequence: Optional[str]
    usage: TokenUsage
    request_id: Optional[str] = None
    raw: Optional[Any] = None               # Original anthropic SDK response object

    @property
    def text(self) -> str:
        """Concatenate all text blocks into a single string."""
        return "".join(b.text for b in self.content if isinstance(b, TextBlock))

    @property
    def thinking(self) -> str:
        """Concatenate all thinking blocks."""
        return "".join(b.thinking for b in self.content if isinstance(b, ThinkingBlock))

    @property
    def tool_calls(self) -> list[ToolCall]:
        """Extract all tool use blocks as ToolCall objects."""
        return [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in self.content if isinstance(b, ToolUseBlock)
        ]

    @property
    def has_tool_calls(self) -> bool:
        return any(isinstance(b, ToolUseBlock) for b in self.content)

    @property
    def has_thinking(self) -> bool:
        return any(isinstance(b, ThinkingBlock) for b in self.content)


# ---------------------------------------------------------------------------
# Stream events
# ---------------------------------------------------------------------------

@dataclass
class StreamToken:
    """A single token/text delta received during streaming."""
    text: str
    index: int = 0


@dataclass
class StreamThinkingToken:
    """A thinking delta received during streaming."""
    thinking: str
    index: int = 0


@dataclass
class StreamEvent:
    """A raw stream event from the API."""
    type: StreamEventType
    data: Any = None


@dataclass
class StreamComplete:
    """
    Emitted when a stream finishes.
    Contains the full assembled response.
    """
    response: ClaudeResponse


# ---------------------------------------------------------------------------
# Session / conversation
# ---------------------------------------------------------------------------

@dataclass
class Session:
    """A conversation session with its own history and config overrides."""
    id: str
    history: list[Message] = field(default_factory=list)
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    token_usage: SessionTokenUsage = field(default_factory=SessionTokenUsage)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, message: Message) -> None:
        self.history.append(message)
        self.updated_at = time.time()

    def clear_history(self) -> None:
        self.history.clear()
        self.updated_at = time.time()

    @property
    def message_count(self) -> int:
        return len(self.history)


# ---------------------------------------------------------------------------
# Request input — what the outer machine sends IN
# ---------------------------------------------------------------------------

@dataclass
class SendRequest:
    """
    Full specification for a single send operation.
    Every parameter is optional — config/session defaults fill in the gaps.
    """
    # Content
    content: Union[str, list[ContentBlock]]
    session_id: Optional[str] = None

    # Model params (override config/session defaults)
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[list[str]] = None
    system: Optional[str] = None

    # Streaming
    stream: Optional[bool] = None

    # Tools
    tools: Optional[list[str]] = None       # Tool names to enable for this request
    tool_choice: Optional[Union[ToolChoice, str]] = None

    # Extended thinking
    thinking_enabled: Optional[bool] = None
    thinking_budget_tokens: Optional[int] = None

    # Metadata
    metadata: Optional[dict[str, str]] = None

    # Service tier
    service_tier: Optional[str] = None

    # Beta features (list of beta header strings)
    betas: Optional[list[str]] = None

    # Prefill — assistant turn prefill
    prefill: Optional[str] = None

    # Extra pass-through kwargs for the API (escape hatch)
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Batch models
# ---------------------------------------------------------------------------

@dataclass
class BatchRequest:
    """A single request within a batch."""
    custom_id: str
    content: Union[str, list[ContentBlock]]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[list[str]] = None
    system: Optional[str] = None
    tools: Optional[list[str]] = None
    tool_choice: Optional[Union[ToolChoice, str]] = None
    metadata: Optional[dict[str, str]] = None
    betas: Optional[list[str]] = None


@dataclass
class BatchResult:
    """Result for a single request within a completed batch."""
    custom_id: str
    status: BatchRequestStatus
    response: Optional[ClaudeResponse] = None
    error: Optional[dict[str, Any]] = None


@dataclass
class BatchStatus:
    """Status of a batch job."""
    id: str
    processing_status: BatchProcessingStatus
    request_counts: dict[str, int] = field(default_factory=dict)
    created_at: Optional[float] = None
    ended_at: Optional[float] = None
    expires_at: Optional[float] = None
    raw: Optional[Any] = None


# ---------------------------------------------------------------------------
# File models
# ---------------------------------------------------------------------------

@dataclass
class UploadedFile:
    """A file that has been uploaded to the Files API."""
    file_id: str
    filename: str
    media_type: str
    size_bytes: Optional[int] = None
    created_at: Optional[float] = None
    raw: Optional[Any] = None


# ---------------------------------------------------------------------------
# Config snapshot — a read-only view of current effective config
# ---------------------------------------------------------------------------

@dataclass
class ConfigSnapshot:
    """
    Point-in-time snapshot of the effective configuration.
    Exposed as a readable output connector on the box surface.
    """
    model: str
    max_tokens: int
    temperature: Optional[float]
    top_p: Optional[float]
    top_k: Optional[int]
    stream: bool
    system_prompt: Optional[str]
    thinking_enabled: bool
    thinking_budget_tokens: Optional[int]
    tool_choice: str
    auto_run_tools: bool
    max_tool_iterations: int
    multi_session: bool
    max_history_messages: Optional[int]
    log_level: str
    raw: dict[str, Any] = field(default_factory=dict)
