"""
claudebox.exceptions
====================
Complete exception hierarchy for ClaudeBox.

Every error that can occur — internally, in the API, in user code, in tools,
in streaming, in config — has its own exception type here. Nothing is swallowed
silently. Everything is catchable at whatever granularity the outer machine needs.

Hierarchy:
    ClaudeBoxError                          # Base for everything
    ├── ConfigError                         # Config file issues
    │   ├── ConfigNotFoundError
    │   ├── ConfigParseError
    │   └── ConfigValidationError
    ├── ClientError                         # Client initialization issues
    │   ├── AuthenticationError
    │   └── ClientNotInitializedError
    ├── APIError                            # Errors from the Anthropic API
    │   ├── APIConnectionError
    │   ├── APITimeoutError
    │   ├── RateLimitError
    │   ├── BadRequestError
    │   ├── AuthorizationError
    │   ├── PermissionDeniedError
    │   ├── NotFoundError
    │   ├── UnprocessableEntityError
    │   ├── InternalServerError
    │   └── OverloadedError
    ├── ConversationError                   # Conversation/session issues
    │   ├── SessionNotFoundError
    │   ├── SessionAlreadyExistsError
    │   ├── HistoryTruncationError
    │   └── InvalidMessageRoleError
    ├── StreamingError                      # Streaming issues
    │   ├── StreamNotStartedError
    │   ├── StreamAlreadyConsumedError
    │   └── StreamInterruptedError
    ├── ToolError                           # Tool use issues
    │   ├── ToolNotFoundError
    │   ├── ToolAlreadyRegisteredError
    │   ├── ToolExecutionError
    │   ├── ToolValidationError
    │   ├── ToolTimeoutError
    │   └── MaxToolIterationsError
    ├── VisionError                         # Image/vision issues
    │   ├── UnsupportedMediaTypeError
    │   ├── ImageTooLargeError
    │   └── ImageLoadError
    ├── FileError                           # Files API issues
    │   ├── FileUploadError
    │   ├── FileNotFoundError
    │   └── FileAPINotEnabledError
    ├── BatchError                          # Batch processing issues
    │   ├── BatchCreationError
    │   ├── BatchPollError
    │   └── BatchResultError
    ├── EventError                          # Event bus issues
    │   ├── EventHandlerError
    │   └── UnknownEventError
    └── ThinkingError                       # Extended thinking issues
        └── ThinkingBudgetError
"""

from __future__ import annotations
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class ClaudeBoxError(Exception):
    """Base exception for all ClaudeBox errors."""

    def __init__(self, message: str, *, cause: Optional[BaseException] = None, context: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.context = context or {}
        if cause:
            self.__cause__ = cause

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


# ---------------------------------------------------------------------------
# Config errors
# ---------------------------------------------------------------------------

class ConfigError(ClaudeBoxError):
    """Base for all configuration-related errors."""


class ConfigNotFoundError(ConfigError):
    """Config file could not be located at the expected path."""


class ConfigParseError(ConfigError):
    """Config file exists but could not be parsed (invalid YAML, etc.)."""


class ConfigValidationError(ConfigError):
    """Config file parsed successfully but contains invalid values."""

    def __init__(self, message: str, *, field: Optional[str] = None, value: Any = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


# ---------------------------------------------------------------------------
# Client errors
# ---------------------------------------------------------------------------

class ClientError(ClaudeBoxError):
    """Base for client initialization and setup errors."""


class AuthenticationError(ClientError):
    """API key is missing, invalid, or expired."""


class ClientNotInitializedError(ClientError):
    """An operation was attempted before the client was initialized."""


# ---------------------------------------------------------------------------
# API errors — mirror Anthropic SDK hierarchy but wrapped
# ---------------------------------------------------------------------------

class APIError(ClaudeBoxError):
    """Base for all errors returned by the Anthropic API."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, request_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.request_id = request_id


class APIConnectionError(APIError):
    """Could not connect to the Anthropic API (network issue, DNS failure, etc.)."""


class APITimeoutError(APIError):
    """Request to the Anthropic API timed out."""


class RateLimitError(APIError):
    """HTTP 429 — rate limit exceeded."""

    def __init__(self, message: str, *, retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class BadRequestError(APIError):
    """HTTP 400 — malformed request."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class APIAuthorizationError(APIError):
    """HTTP 401 — unauthorized."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class PermissionDeniedError(APIError):
    """HTTP 403 — permission denied."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class APINotFoundError(APIError):
    """HTTP 404 — resource not found."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class UnprocessableEntityError(APIError):
    """HTTP 422 — request was well-formed but semantically invalid."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class InternalServerError(APIError):
    """HTTP 5xx — Anthropic server error."""


class OverloadedError(APIError):
    """HTTP 529 — Anthropic API is temporarily overloaded."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=529, **kwargs)


# ---------------------------------------------------------------------------
# Conversation errors
# ---------------------------------------------------------------------------

class ConversationError(ClaudeBoxError):
    """Base for conversation and session management errors."""


class SessionNotFoundError(ConversationError):
    """Requested session ID does not exist."""

    def __init__(self, message: str, *, session_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.session_id = session_id


class SessionAlreadyExistsError(ConversationError):
    """Attempted to create a session with an ID that already exists."""

    def __init__(self, message: str, *, session_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.session_id = session_id


class HistoryTruncationError(ConversationError):
    """History could not be truncated safely without breaking the conversation."""


class InvalidMessageRoleError(ConversationError):
    """A message was added with an invalid role."""

    def __init__(self, message: str, *, role: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.role = role


# ---------------------------------------------------------------------------
# Streaming errors
# ---------------------------------------------------------------------------

class StreamingError(ClaudeBoxError):
    """Base for streaming-related errors."""


class StreamNotStartedError(StreamingError):
    """Attempted to consume a stream that has not been started."""


class StreamAlreadyConsumedError(StreamingError):
    """Attempted to consume a stream that has already been fully consumed."""


class StreamInterruptedError(StreamingError):
    """Stream was interrupted before completion."""

    def __init__(self, message: str, *, partial_text: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.partial_text = partial_text


# ---------------------------------------------------------------------------
# Tool errors
# ---------------------------------------------------------------------------

class ToolError(ClaudeBoxError):
    """Base for tool use errors."""


class ToolNotFoundError(ToolError):
    """Claude requested a tool that is not registered."""

    def __init__(self, message: str, *, tool_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name


class ToolAlreadyRegisteredError(ToolError):
    """Attempted to register a tool with a name that is already taken."""

    def __init__(self, message: str, *, tool_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name


class ToolExecutionError(ToolError):
    """A tool raised an exception during execution."""

    def __init__(self, message: str, *, tool_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name


class ToolValidationError(ToolError):
    """Tool input failed schema validation before execution."""

    def __init__(self, message: str, *, tool_name: Optional[str] = None, validation_errors: Optional[list] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.validation_errors = validation_errors or []


class ToolTimeoutError(ToolError):
    """A tool exceeded its allowed execution time."""

    def __init__(self, message: str, *, tool_name: Optional[str] = None, timeout: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.timeout = timeout


class MaxToolIterationsError(ToolError):
    """The tool use loop exceeded the configured maximum number of iterations."""

    def __init__(self, message: str, *, iterations: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.iterations = iterations


# ---------------------------------------------------------------------------
# Vision errors
# ---------------------------------------------------------------------------

class VisionError(ClaudeBoxError):
    """Base for image/vision input errors."""


class UnsupportedMediaTypeError(VisionError):
    """Image media type is not supported by the API."""

    def __init__(self, message: str, *, media_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.media_type = media_type


class ImageTooLargeError(VisionError):
    """Image exceeds the configured or API maximum size."""

    def __init__(self, message: str, *, size_bytes: Optional[int] = None, max_bytes: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes


class ImageLoadError(VisionError):
    """Image could not be loaded or encoded."""


# ---------------------------------------------------------------------------
# File errors
# ---------------------------------------------------------------------------

class FileError(ClaudeBoxError):
    """Base for Files API errors."""


class FileUploadError(FileError):
    """File could not be uploaded to the Files API."""


class FilesAPINotFoundError(FileError):
    """Referenced file ID does not exist in the Files API."""

    def __init__(self, message: str, *, file_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_id = file_id


class FileAPINotEnabledError(FileError):
    """Files API beta feature is not enabled in config."""


# ---------------------------------------------------------------------------
# Batch errors
# ---------------------------------------------------------------------------

class BatchError(ClaudeBoxError):
    """Base for Message Batches API errors."""


class BatchCreationError(BatchError):
    """Batch could not be created."""


class BatchPollError(BatchError):
    """Error occurred while polling batch status."""

    def __init__(self, message: str, *, batch_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.batch_id = batch_id


class BatchResultError(BatchError):
    """Error occurred while retrieving batch results."""

    def __init__(self, message: str, *, batch_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.batch_id = batch_id


# ---------------------------------------------------------------------------
# Event errors
# ---------------------------------------------------------------------------

class EventError(ClaudeBoxError):
    """Base for event bus errors."""


class EventHandlerError(EventError):
    """An event handler raised an exception during execution."""

    def __init__(self, message: str, *, event_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.event_name = event_name


class UnknownEventError(EventError):
    """Attempted to subscribe to or emit an unknown event name."""

    def __init__(self, message: str, *, event_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.event_name = event_name


# ---------------------------------------------------------------------------
# Thinking errors
# ---------------------------------------------------------------------------

class ThinkingError(ClaudeBoxError):
    """Base for extended thinking errors."""


class ThinkingBudgetError(ThinkingError):
    """Extended thinking budget_tokens value is invalid."""

    def __init__(self, message: str, *, budget_tokens: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.budget_tokens = budget_tokens


# ---------------------------------------------------------------------------
# Mapping from Anthropic SDK status codes to ClaudeBox exceptions
# ---------------------------------------------------------------------------

_STATUS_CODE_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: APIAuthorizationError,
    403: PermissionDeniedError,
    404: APINotFoundError,
    422: UnprocessableEntityError,
    429: RateLimitError,
    529: OverloadedError,
}


def wrap_anthropic_error(exc: Exception) -> ClaudeBoxError:
    """
    Convert an anthropic SDK exception into the corresponding ClaudeBox exception.
    Preserves the original as __cause__ so full tracebacks are always accessible.
    """
    import anthropic as _anthropic

    if isinstance(exc, _anthropic.APIConnectionError):
        return APIConnectionError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.APITimeoutError):
        return APITimeoutError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.RateLimitError):
        return RateLimitError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.AuthenticationError):
        return AuthenticationError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.PermissionDeniedError):
        return PermissionDeniedError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.NotFoundError):
        return APINotFoundError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.UnprocessableEntityError):
        return UnprocessableEntityError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.BadRequestError):
        return BadRequestError(str(exc), cause=exc)
    if isinstance(exc, _anthropic.InternalServerError):
        return InternalServerError(str(exc), status_code=getattr(exc, 'status_code', None), cause=exc)
    if isinstance(exc, _anthropic.APIStatusError):
        status = getattr(exc, 'status_code', None)
        cls = _STATUS_CODE_MAP.get(status, APIError)
        return cls(str(exc), status_code=status, cause=exc)
    if isinstance(exc, _anthropic.APIError):
        return APIError(str(exc), cause=exc)

    # Anything else — wrap as base ClaudeBoxError
    return ClaudeBoxError(str(exc), cause=exc)
