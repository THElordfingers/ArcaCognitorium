"""
claudebox
=========
The ultimate do-it-all Claude API engine block.

Drop it into any project. Wire up the connectors you need.
Everything is exposed. Nothing is hidden. Nothing is excluded.

QUICK START:
    from claudebox import ClaudeBox

    box = ClaudeBox()
    response = box.send("Hello, Claude")
    print(response.text)

STREAMING:
    box.on_token(lambda t: print(t.text, end="", flush=True))
    response = box.send("Tell me a story")

    # Generator style
    for token in box.stream("Tell me a story"):
        print(token, end="", flush=True)

ASYNC:
    response = await box.send_async("Hello")

    async for token in box.stream_async("Hello"):
        print(token, end="")

TOOLS:
    @box.tool
    def get_weather(location: str) -> str:
        return "Sunny, 72F"

    response = box.send("What's the weather in London?")

SESSIONS:
    box.send("Hello", session_id="alice")
    box.send("Hello", session_id="bob")

VISION:
    from claudebox import ImageBlock, ImageSource
    img = ImageBlock(source=ImageSource(type="base64", media_type="image/png", data=b64_data))
    response = box.send([img, TextBlock(text="What's in this image?")])

CONFIG:
    box.config_snapshot()     # inspect current config
    box.reload_config()       # hot-reload claudebox.config.yaml

EVENTS — every output port:
    box.on_token(handler)
    box.on_response(handler)
    box.on_tool_call(handler)
    box.on_tool_result(handler)
    box.on_error(handler)
    box.on_token_usage(handler)
    box.on_stream_start(handler)
    box.on_stream_end(handler)
    box.on_session_created(handler)
    box.on_batch_complete(handler)
    ... and many more (see EventName enum)

See claudebox.config.yaml for every configurable option.
"""

# =============================================================================
# Public surface — everything the outer machine might need
# =============================================================================

# The box itself
from .client import ClaudeBox

# Config
from .config import Config

# Events
from .events import EventBus, EventName

# Models — inputs
from .models import (
    BatchRequest,
    ContentBlock,
    DocumentBlock,
    DocumentSource,
    ImageBlock,
    ImageSource,
    MediaType,
    Message,
    Role,
    SendRequest,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
)

# Models — outputs
from .models import (
    BatchResult,
    BatchRequestStatus,
    BatchStatus,
    BatchProcessingStatus,
    ClaudeResponse,
    ConfigSnapshot,
    ContentBlockType,
    RedactedThinkingBlock,
    Session,
    SessionTokenUsage,
    StopReason,
    StreamComplete,
    StreamEvent,
    StreamEventType,
    StreamThinkingToken,
    StreamToken,
    ThinkingBlock,
    ToolCall,
    ToolDefinition,
    ToolResult,
    TokenUsage,
    UploadedFile,
)

# Tools
from .tools import ToolRegistry

# Conversation
from .conversation import ConversationManager

# Exceptions — every error type is importable at the top level
from .exceptions import (
    APIAuthorizationError,
    APIConnectionError,
    APIError,
    APINotFoundError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    BatchCreationError,
    BatchError,
    BatchPollError,
    BatchResultError,
    ClaudeBoxError,
    ClientError,
    ClientNotInitializedError,
    ConfigError,
    ConfigNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    ConversationError,
    EventError,
    EventHandlerError,
    FileAPINotEnabledError,
    FileError,
    FilesAPINotFoundError,
    FileUploadError,
    HistoryTruncationError,
    ImageLoadError,
    ImageTooLargeError,
    InternalServerError,
    InvalidMessageRoleError,
    MaxToolIterationsError,
    OverloadedError,
    PermissionDeniedError,
    RateLimitError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
    StreamAlreadyConsumedError,
    StreamInterruptedError,
    StreamingError,
    StreamNotStartedError,
    ThinkingBudgetError,
    ThinkingError,
    ToolAlreadyRegisteredError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolTimeoutError,
    ToolValidationError,
    UnknownEventError,
    UnprocessableEntityError,
    UnsupportedMediaTypeError,
    VisionError,
    wrap_anthropic_error,
)

__version__ = "0.1.0"
__author__ = "ClaudeBox"
__all__ = [
    # Core
    "ClaudeBox",
    "Config",
    # Events
    "EventBus",
    "EventName",
    # Input models
    "BatchRequest",
    "ContentBlock",
    "DocumentBlock",
    "DocumentSource",
    "ImageBlock",
    "ImageSource",
    "MediaType",
    "Message",
    "Role",
    "SendRequest",
    "TextBlock",
    "ToolResultBlock",
    "ToolUseBlock",
    # Output models
    "BatchResult",
    "BatchRequestStatus",
    "BatchStatus",
    "BatchProcessingStatus",
    "ClaudeResponse",
    "ConfigSnapshot",
    "ContentBlockType",
    "RedactedThinkingBlock",
    "Session",
    "SessionTokenUsage",
    "StopReason",
    "StreamComplete",
    "StreamEvent",
    "StreamEventType",
    "StreamThinkingToken",
    "StreamToken",
    "ThinkingBlock",
    "ToolCall",
    "ToolDefinition",
    "ToolResult",
    "TokenUsage",
    "UploadedFile",
    # Internal components (for advanced use)
    "ToolRegistry",
    "ConversationManager",
    # Exceptions
    "APIAuthorizationError",
    "APIConnectionError",
    "APIError",
    "APINotFoundError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "BatchCreationError",
    "BatchError",
    "BatchPollError",
    "BatchResultError",
    "ClaudeBoxError",
    "ClientError",
    "ClientNotInitializedError",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigParseError",
    "ConfigValidationError",
    "ConversationError",
    "EventError",
    "EventHandlerError",
    "FileAPINotEnabledError",
    "FileError",
    "FilesAPINotFoundError",
    "FileUploadError",
    "HistoryTruncationError",
    "ImageLoadError",
    "ImageTooLargeError",
    "InternalServerError",
    "InvalidMessageRoleError",
    "MaxToolIterationsError",
    "OverloadedError",
    "PermissionDeniedError",
    "RateLimitError",
    "SessionAlreadyExistsError",
    "SessionNotFoundError",
    "StreamAlreadyConsumedError",
    "StreamInterruptedError",
    "StreamingError",
    "StreamNotStartedError",
    "ThinkingBudgetError",
    "ThinkingError",
    "ToolAlreadyRegisteredError",
    "ToolError",
    "ToolExecutionError",
    "ToolNotFoundError",
    "ToolTimeoutError",
    "ToolValidationError",
    "UnknownEventError",
    "UnprocessableEntityError",
    "UnsupportedMediaTypeError",
    "VisionError",
    "wrap_anthropic_error",
]
