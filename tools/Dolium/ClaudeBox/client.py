"""
claudebox.client
================
ClaudeBox — the engine block.

This is the box. It owns all internal components and exposes every
input port (methods) and output port (events + return values) on its surface.

USAGE:
    from claudebox import ClaudeBox

    box = ClaudeBox()                          # loads claudebox.config.yaml
    box = ClaudeBox("path/to/config.yaml")     # explicit config path

    # Send a message — returns full ClaudeResponse
    response = box.send("Hello, Claude")

    # Send with streaming — tokens fire via event bus AND return value streams
    box.on_token(lambda t: print(t.text, end="", flush=True))
    response = box.send("Tell me a story")

    # Async
    response = await box.send_async("Hello")

    # Threaded (for GUIs)
    box.send_threaded("Hello", on_complete=my_callback)

    # Generators
    for token in box.stream("Hello"):
        print(token, end="")

    async for token in box.stream_async("Hello"):
        print(token, end="")

    # Tools
    @box.tool
    def get_weather(location: str) -> str:
        return "Sunny, 72F"

    # Sessions
    box.send("Hello", session_id="alice")
    box.send("Hello", session_id="bob")

    # Batch
    results = box.run_batch([...])

    # Config inspection
    cfg = box.config_snapshot()
    box.reload_config()
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Iterator, Optional, Union

import anthropic
import httpx

from .config import Config
from .conversation import ConversationManager
from .events import EventBus, EventMixin, EventName
from .exceptions import (
    AuthenticationError,
    BatchCreationError,
    BatchPollError,
    BatchResultError,
    ClientNotInitializedError,
    FileAPINotEnabledError,
    FileUploadError,
    MaxToolIterationsError,
    wrap_anthropic_error,
)
from .models import (
    BatchRequest,
    BatchResult,
    BatchRequestStatus,
    BatchStatus,
    BatchProcessingStatus,
    ClaudeResponse,
    ConfigSnapshot,
    ContentBlock,
    Message,
    Role,
    SendRequest,
    Session,
    TextBlock,
    TokenUsage,
    ToolCall,
    ToolResultBlock,
    UploadedFile,
)
from .streaming import StreamHandler, _parse_response
from .tools import ToolRegistry

logger = logging.getLogger("claudebox")


class ClaudeBox(EventMixin):
    """
    The engine block.

    Every feature of the Anthropic Claude API is available through this single
    class. Drop it into any project, wire up the connectors you need.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        *,
        # Allow any config option to be overridden at init time
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        stream: Optional[bool] = None,
    ):
        """
        Initialize ClaudeBox.

        Args:
            config_path:   Path to claudebox.config.yaml. If None, auto-searches
                           for the file in cwd and home directory.
            api_key:       Override config api_key at init time.
            model:         Override config model at init time.
            system_prompt: Override config system.prompt at init time.
            max_tokens:    Override config model.max_tokens at init time.
            stream:        Override config streaming.enabled at init time.
        """
        # Load config
        self._config = Config.load(config_path)
        self._apply_init_overrides(api_key, model, system_prompt, max_tokens, stream)

        # Set up logging
        self._setup_logging()

        # Initialize event bus
        self._bus = EventBus(
            enabled=self._config.events.get("enabled", True),
            async_handlers=self._config.events.get("async_handlers", False),
            thread_pool_size=self._config.events.get("handler_thread_pool_size", 4),
            suppress_handler_errors=self._config.events.get("suppress_handler_errors", True),
            allow_unknown_events=self._config.events.get("allow_unknown_events", False),
        )

        # Initialize internal components
        self._conversation = ConversationManager(self._config, self._bus)
        self._tools = ToolRegistry(self._config, self._bus)
        self._stream_handler = StreamHandler(self._config, self._bus)

        # Initialize Anthropic clients (sync + async)
        self._sync_client: Optional[anthropic.Anthropic] = None
        self._async_client: Optional[anthropic.AsyncAnthropic] = None
        self._init_clients()

        self._bus.emit(EventName.BOX_INITIALIZED, self)
        self._bus.emit(EventName.CONFIG_LOADED, self._config)
        logger.info(f"ClaudeBox initialized — model={self._config.model.get('model')}")

    # ------------------------------------------------------------------
    # Client initialization
    # ------------------------------------------------------------------

    def _apply_init_overrides(self, api_key, model, system_prompt, max_tokens, stream) -> None:
        if api_key:
            self._config._data["api"]["api_key"] = api_key
        if model:
            self._config._data["model"]["model"] = model
        if system_prompt is not None:
            self._config._data["system"]["prompt"] = system_prompt
        if max_tokens:
            self._config._data["model"]["max_tokens"] = max_tokens
        if stream is not None:
            self._config._data["streaming"]["enabled"] = stream
        self._config._build_sections()

    def _init_clients(self) -> None:
        """Initialize sync and async Anthropic clients."""
        resolved_key = self._config.get_api_key()
        if not resolved_key:
            raise AuthenticationError(
                "No API key found. Set ANTHROPIC_API_KEY env var, "
                "or configure api.api_key in claudebox.config.yaml."
            )

        timeout = httpx.Timeout(
            self._config.connection.get("timeout_total", 600.0),
            connect=self._config.connection.get("timeout_connect", 10.0),
            read=self._config.connection.get("timeout_read", 300.0),
            write=self._config.connection.get("timeout_write", 30.0),
        )

        http_kwargs: dict[str, Any] = {}
        proxy = self._config.connection.get("proxy")
        if proxy:
            http_kwargs["proxy"] = proxy

        http_client = anthropic.DefaultHttpxClient(
            follow_redirects=self._config.connection.get("follow_redirects", True),
            limits=httpx.Limits(
                max_connections=self._config.connection.get("max_connections", 100),
                max_keepalive_connections=self._config.connection.get("max_keepalive_connections", 20),
                keepalive_expiry=self._config.connection.get("keepalive_expiry", 5.0),
            ),
            **http_kwargs,
        )

        client_kwargs: dict[str, Any] = {
            "api_key": resolved_key,
            "max_retries": self._config.connection.get("max_retries", 2),
            "timeout": timeout,
            "default_headers": dict(self._config.api.get("default_headers") or {}),
            "default_query": dict(self._config.api.get("default_query") or {}),
            "http_client": http_client,
        }

        base_url = self._config.api.get("base_url")
        if base_url:
            client_kwargs["base_url"] = base_url

        auth_token = self._config.api.get("auth_token")
        if auth_token:
            client_kwargs["auth_token"] = auth_token
            client_kwargs.pop("api_key", None)

        platform = self._config.get_platform()

        if platform == "bedrock":
            bc = self._config.platform.get("bedrock") or {}
            self._sync_client = anthropic.AnthropicBedrock(
                aws_region=bc.get("aws_region"),
                aws_access_key=bc.get("aws_access_key"),
                aws_secret_key=bc.get("aws_secret_key"),
                aws_session_token=bc.get("aws_session_token"),
                aws_profile=bc.get("aws_profile"),
                timeout=timeout,
                max_retries=client_kwargs["max_retries"],
            )
        elif platform == "vertex":
            vc = self._config.platform.get("vertex") or {}
            self._sync_client = anthropic.AnthropicVertex(
                project_id=vc.get("project_id"),
                region=vc.get("region", "us-east5"),
                timeout=timeout,
                max_retries=client_kwargs["max_retries"],
            )
        else:
            self._sync_client = anthropic.Anthropic(**client_kwargs)
            # Async client (same config, async variant)
            async_http = anthropic.DefaultAsyncHttpxClient(
                follow_redirects=self._config.connection.get("follow_redirects", True),
                limits=httpx.Limits(
                    max_connections=self._config.connection.get("max_connections", 100),
                    max_keepalive_connections=self._config.connection.get("max_keepalive_connections", 20),
                    keepalive_expiry=self._config.connection.get("keepalive_expiry", 5.0),
                ),
                **http_kwargs,
            )
            async_kwargs = {**client_kwargs, "http_client": async_http}
            self._async_client = anthropic.AsyncAnthropic(**async_kwargs)

        # Set SDK log level via env var
        sdk_log = self._config.logging.get("sdk_log_level", "off")
        if sdk_log != "off":
            os.environ["ANTHROPIC_LOG"] = sdk_log

    def _setup_logging(self) -> None:
        log_cfg = self._config.logging
        level_str = log_cfg.get("level", "warning").upper()
        if level_str == "OFF":
            level = logging.CRITICAL + 1
        else:
            level = getattr(logging, level_str, logging.WARNING)

        logger_name = log_cfg.get("logger_name", "claudebox")
        cb_logger = logging.getLogger(logger_name)
        cb_logger.setLevel(level)

        if not cb_logger.handlers:
            fmt = log_cfg.get("log_format", "%(asctime)s [%(name)s] %(levelname)s: %(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt))
            cb_logger.addHandler(handler)

        if log_cfg.get("log_to_file", False):
            from logging.handlers import RotatingFileHandler
            fh = RotatingFileHandler(
                log_cfg.get("log_file_path", "claudebox.log"),
                maxBytes=log_cfg.get("log_file_max_bytes", 10485760),
                backupCount=log_cfg.get("log_file_backup_count", 3),
            )
            fh.setFormatter(logging.Formatter(log_cfg.get("log_format", "")))
            cb_logger.addHandler(fh)

    # ------------------------------------------------------------------
    # Core send — sync
    # ------------------------------------------------------------------

    def send(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[list[str]] = None,
        system: Optional[str] = None,
        stream: Optional[bool] = None,
        tools: Optional[list[str]] = None,
        tool_choice: Optional[str] = None,
        thinking_enabled: Optional[bool] = None,
        thinking_budget_tokens: Optional[int] = None,
        metadata: Optional[dict[str, str]] = None,
        service_tier: Optional[str] = None,
        betas: Optional[list[str]] = None,
        prefill: Optional[str] = None,
        **extra_kwargs,
    ) -> ClaudeResponse:
        """
        Send a message and return a ClaudeResponse.

        All parameters are optional — config and session defaults fill in the gaps.
        Per-request values override session which overrides config.

        Returns:
            ClaudeResponse — always, whether streaming or not.
            If streaming is enabled, tokens are fired via on_token events
            while this method blocks until complete.
        """
        req = SendRequest(
            content=content,
            session_id=session_id,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
            system=system,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            thinking_enabled=thinking_enabled,
            thinking_budget_tokens=thinking_budget_tokens,
            metadata=metadata,
            service_tier=service_tier,
            betas=betas,
            prefill=prefill,
            extra_kwargs=extra_kwargs,
        )
        return self._execute_sync(req)

    def _execute_sync(self, req: SendRequest) -> ClaudeResponse:
        self._conversation.add_user_message(req.content, req.session_id)
        request_kwargs = self._build_request_kwargs(req)

        self._bus.emit(EventName.REQUEST_START, request_kwargs)
        if self._config.logging.get("log_requests", False):
            self._bus.emit(EventName.RAW_REQUEST, request_kwargs)

        use_stream = req.stream if req.stream is not None else self._config.streaming.get("enabled", True)

        try:
            if use_stream:
                thread_mode = self._config.streaming.get("thread_mode", "direct")
                response = self._stream_handler.stream_sync(self._sync_client, request_kwargs)
            else:
                raw = self._sync_client.messages.create(**request_kwargs)
                response = self._stream_handler.parse_non_streaming(raw)
                self._bus.emit(EventName.RESPONSE, response)

        except Exception as e:
            self._bus.emit(EventName.ERROR, e)
            self._bus.emit(EventName.REQUEST_END, {"error": e})
            raise

        self._finalize_response(response, req)
        return response

    # ------------------------------------------------------------------
    # Core send — async
    # ------------------------------------------------------------------

    async def send_async(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[list[str]] = None,
        system: Optional[str] = None,
        stream: Optional[bool] = None,
        tools: Optional[list[str]] = None,
        tool_choice: Optional[str] = None,
        thinking_enabled: Optional[bool] = None,
        thinking_budget_tokens: Optional[int] = None,
        metadata: Optional[dict[str, str]] = None,
        service_tier: Optional[str] = None,
        betas: Optional[list[str]] = None,
        prefill: Optional[str] = None,
        **extra_kwargs,
    ) -> ClaudeResponse:
        """Async version of send(). Use with `await box.send_async(...)`."""
        req = SendRequest(
            content=content,
            session_id=session_id,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
            system=system,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            thinking_enabled=thinking_enabled,
            thinking_budget_tokens=thinking_budget_tokens,
            metadata=metadata,
            service_tier=service_tier,
            betas=betas,
            prefill=prefill,
            extra_kwargs=extra_kwargs,
        )
        return await self._execute_async(req)

    async def _execute_async(self, req: SendRequest) -> ClaudeResponse:
        self._conversation.add_user_message(req.content, req.session_id)
        request_kwargs = self._build_request_kwargs(req)

        await self._bus.emit_async(EventName.REQUEST_START, request_kwargs)
        use_stream = req.stream if req.stream is not None else self._config.streaming.get("enabled", True)

        try:
            if use_stream:
                response = await self._stream_handler.stream_async(self._async_client, request_kwargs)
            else:
                raw = await self._async_client.messages.create(**request_kwargs)
                response = self._stream_handler.parse_non_streaming(raw)
                await self._bus.emit_async(EventName.RESPONSE, response)

        except Exception as e:
            await self._bus.emit_async(EventName.ERROR, e)
            raise

        await self._finalize_response_async(response, req)
        return response

    # ------------------------------------------------------------------
    # Threaded send (for GUI frameworks)
    # ------------------------------------------------------------------

    def send_threaded(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        on_token: Optional[Callable] = None,
        on_complete: Optional[Callable[[ClaudeResponse], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> threading.Thread:
        """
        Send a message in a background thread. Returns immediately.

        Use on_token, on_complete, on_error callbacks — or subscribe to
        bus events before calling. Safe to call from GUI main threads.
        """
        def _run():
            try:
                response = self.send(content, session_id=session_id, **kwargs)
                if on_complete:
                    on_complete(response)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logger.error(f"send_threaded error: {e}", exc_info=e)

        if on_token:
            self._bus.once(EventName.TOKEN, on_token)

        thread = threading.Thread(target=_run, daemon=True, name="claudebox-send")
        thread.start()
        return thread

    # ------------------------------------------------------------------
    # Generator interfaces
    # ------------------------------------------------------------------

    def stream(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> Iterator[str]:
        """
        Sync generator — yields text tokens one at a time.

        Usage:
            for token in box.stream("Tell me a story"):
                print(token, end="", flush=True)
        """
        self._conversation.add_user_message(content, session_id)
        req = SendRequest(content=content, session_id=session_id, **kwargs)
        request_kwargs = self._build_request_kwargs(req)
        yield from self._stream_handler.token_generator(self._sync_client, request_kwargs)

    async def stream_async(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Async generator — yields text tokens one at a time.

        Usage:
            async for token in box.stream_async("Tell me a story"):
                print(token, end="", flush=True)
        """
        self._conversation.add_user_message(content, session_id)
        req = SendRequest(content=content, session_id=session_id, **kwargs)
        request_kwargs = self._build_request_kwargs(req)
        async for token in self._stream_handler.token_generator_async(self._async_client, request_kwargs):
            yield token

    # ------------------------------------------------------------------
    # Tool management — surface connectors
    # ------------------------------------------------------------------

    @property
    def tool(self):
        """Decorator to register a tool. Use as @box.tool or @box.tool(name=...) """
        return self._tools.register

    def register_tool(self, fn: Callable, **kwargs) -> None:
        """Explicitly register a tool function."""
        self._tools.register_tool(fn, **kwargs)

    def unregister_tool(self, name: str) -> None:
        """Remove a registered tool."""
        self._tools.unregister(name)

    def unregister_all_tools(self) -> None:
        """Remove all registered tools."""
        self._tools.unregister_all()

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""
        return self._tools.list_tools()

    # ------------------------------------------------------------------
    # Session management — surface connectors
    # ------------------------------------------------------------------

    def create_session(self, session_id: str, **kwargs) -> Session:
        """Create a new named session."""
        return self._conversation.create_session(session_id, **kwargs)

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its history."""
        self._conversation.delete_session(session_id)

    def clear_history(self, session_id: Optional[str] = None) -> None:
        """Clear message history for a session (or the default session)."""
        self._conversation.clear_history(session_id)

    def get_history(self, session_id: Optional[str] = None) -> list[Message]:
        """Get message history for a session."""
        return self._conversation.get_history(session_id)

    def list_sessions(self) -> list[str]:
        """Return all active session IDs."""
        return self._conversation.list_sessions()

    def get_session(self, session_id: Optional[str] = None) -> Session:
        """Get a Session object by ID."""
        return self._conversation.get_session(session_id)

    def set_session_system_prompt(self, system_prompt: str, session_id: Optional[str] = None) -> None:
        """Set a system prompt override for a specific session."""
        session = self._conversation.get_or_create_session(session_id)
        session.system_prompt = system_prompt

    def get_token_usage(self, session_id: Optional[str] = None) -> TokenUsage:
        """Get cumulative token usage for a session."""
        return self._conversation.get_usage(session_id)

    def get_all_token_usage(self) -> dict[str, TokenUsage]:
        """Get token usage across all sessions."""
        return self._conversation.get_all_usage()

    # ------------------------------------------------------------------
    # Token counting
    # ------------------------------------------------------------------

    def count_tokens(
        self,
        content: Union[str, list[ContentBlock]],
        *,
        session_id: Optional[str] = None,
        system: Optional[str] = None,
        tools: Optional[list[str]] = None,
        model: Optional[str] = None,
    ) -> int:
        """
        Count tokens for a message without sending it.
        Returns the input_tokens count.
        """
        resolved_model = model or self._config.model.get("model")
        messages = self._conversation.get_history_as_dicts(session_id)
        messages.append({"role": "user", "content": content if isinstance(content, str) else [b for b in content]})

        kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": messages,
        }
        resolved_system = system or self._conversation.build_system_prompt(session_id)
        if resolved_system:
            kwargs["system"] = resolved_system
        if tools:
            kwargs["tools"] = self._tools.to_api_list(tools)

        try:
            result = self._sync_client.messages.count_tokens(**kwargs)
            return result.input_tokens
        except Exception as e:
            raise wrap_anthropic_error(e)

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def submit_batch(self, requests: list[BatchRequest]) -> BatchStatus:
        """
        Submit a list of requests as a message batch.
        Returns immediately with BatchStatus (including batch ID).
        """
        api_requests = []
        for req in requests:
            resolved_model = req.model or self._config.model.get("model")
            resolved_max_tokens = req.max_tokens or self._config.model.get("max_tokens", 1024)

            content = req.content if isinstance(req.content, str) else req.content
            params: dict[str, Any] = {
                "model": resolved_model,
                "max_tokens": resolved_max_tokens,
                "messages": [{"role": "user", "content": content}],
            }
            if req.temperature is not None:
                params["temperature"] = req.temperature
            if req.top_p is not None:
                params["top_p"] = req.top_p
            if req.top_k is not None:
                params["top_k"] = req.top_k
            if req.stop_sequences:
                params["stop_sequences"] = req.stop_sequences
            if req.system:
                params["system"] = req.system
            if req.tools:
                params["tools"] = self._tools.to_api_list(req.tools)
            if req.metadata:
                params["metadata"] = req.metadata

            betas = req.betas or self._config.get_active_beta_headers()
            api_requests.append({
                "custom_id": req.custom_id,
                "params": params,
            })

        try:
            raw_batch = self._sync_client.messages.batches.create(requests=api_requests)
        except Exception as e:
            raise BatchCreationError(str(e), cause=e)

        status = BatchStatus(
            id=raw_batch.id,
            processing_status=BatchProcessingStatus(raw_batch.processing_status),
            raw=raw_batch,
        )
        self._bus.emit(EventName.BATCH_CREATED, status)
        return status

    def poll_batch(self, batch_id: str) -> BatchStatus:
        """Check the current status of a batch."""
        try:
            raw = self._sync_client.messages.batches.retrieve(batch_id)
        except Exception as e:
            raise BatchPollError(str(e), batch_id=batch_id, cause=e)

        status = BatchStatus(
            id=raw.id,
            processing_status=BatchProcessingStatus(raw.processing_status),
            raw=raw,
        )
        self._bus.emit(EventName.BATCH_POLL, status)
        return status

    def wait_for_batch(self, batch_id: str) -> BatchStatus:
        """
        Poll until the batch is complete. Blocks the calling thread.
        Respects batches.poll_interval_seconds and batches.max_poll_wait_seconds from config.
        """
        interval = self._config.batches.get("poll_interval_seconds", 60)
        max_wait = self._config.batches.get("max_poll_wait_seconds")
        start = time.time()

        while True:
            status = self.poll_batch(batch_id)
            if status.processing_status == BatchProcessingStatus.ENDED:
                self._bus.emit(EventName.BATCH_COMPLETE, status)
                return status
            if max_wait and (time.time() - start) > max_wait:
                raise BatchPollError(
                    f"Batch '{batch_id}' did not complete within {max_wait}s",
                    batch_id=batch_id,
                )
            time.sleep(interval)

    def get_batch_results(self, batch_id: str) -> list[BatchResult]:
        """Retrieve all results from a completed batch."""
        results = []
        try:
            for entry in self._sync_client.messages.batches.results(batch_id):
                status = BatchRequestStatus(entry.result.type)
                response = None
                error = None
                if status == BatchRequestStatus.SUCCEEDED:
                    response = _parse_response(entry.result.message)
                else:
                    error = {"type": entry.result.type, "error": getattr(entry.result, "error", None)}

                result = BatchResult(
                    custom_id=entry.custom_id,
                    status=status,
                    response=response,
                    error=error,
                )
                self._bus.emit(EventName.BATCH_RESULT, result)
                results.append(result)
        except Exception as e:
            raise BatchResultError(str(e), batch_id=batch_id, cause=e)
        return results

    def run_batch(self, requests: list[BatchRequest]) -> list[BatchResult]:
        """
        Submit a batch, wait for completion, and return all results.
        Convenience wrapper for submit_batch + wait_for_batch + get_batch_results.
        """
        status = self.submit_batch(requests)
        if self._config.batches.get("auto_poll", True):
            status = self.wait_for_batch(status.id)
        return self.get_batch_results(status.id)

    # ------------------------------------------------------------------
    # Files API
    # ------------------------------------------------------------------

    def upload_file(
        self,
        file,  # Path, (filename, bytes, mime_type) tuple, or BinaryIO
        *,
        media_type: Optional[str] = None,
    ) -> UploadedFile:
        """Upload a file to the Files API. Returns an UploadedFile with file_id."""
        if not self._config.files.get("enabled", False):
            raise FileAPINotEnabledError(
                "Files API is disabled. Set files.enabled=true in claudebox.config.yaml."
            )
        beta = self._config.files.get("beta_header", "files-api-2025-04-14")
        try:
            result = self._sync_client.beta.files.upload(file=file, betas=[beta])
            uploaded = UploadedFile(
                file_id=result.id,
                filename=getattr(result, "filename", str(file)),
                media_type=media_type or self._config.files.get("default_upload_media_type", "application/octet-stream"),
                raw=result,
            )
            self._bus.emit(EventName.FILE_UPLOADED, uploaded)
            return uploaded
        except Exception as e:
            raise FileUploadError(str(e), cause=e)

    def delete_file(self, file_id: str) -> None:
        """Delete a file from the Files API."""
        beta = self._config.files.get("beta_header", "files-api-2025-04-14")
        try:
            self._sync_client.beta.files.delete(file_id, betas=[beta])
            self._bus.emit(EventName.FILE_DELETED, file_id)
        except Exception as e:
            raise wrap_anthropic_error(e)

    # ------------------------------------------------------------------
    # Config management
    # ------------------------------------------------------------------

    def reload_config(self) -> None:
        """Hot-reload claudebox.config.yaml without restarting."""
        self._config.reload()
        self._bus.emit(EventName.CONFIG_RELOADED, self._config)
        logger.info("Config reloaded")

    def config_snapshot(self) -> ConfigSnapshot:
        """
        Return a read-only snapshot of the current effective configuration.
        Useful for inspection, logging, and debugging.
        """
        return ConfigSnapshot(
            model=self._config.model.get("model", ""),
            max_tokens=self._config.model.get("max_tokens", 1024),
            temperature=self._config.model.get("temperature"),
            top_p=self._config.model.get("top_p"),
            top_k=self._config.model.get("top_k"),
            stream=self._config.streaming.get("enabled", True),
            system_prompt=self._config.system.get("prompt"),
            thinking_enabled=self._config.thinking.get("enabled", False),
            thinking_budget_tokens=self._config.thinking.get("budget_tokens"),
            tool_choice=self._config.tools.get("tool_choice", "auto"),
            auto_run_tools=self._config.tools.get("auto_run_tools", True),
            max_tool_iterations=self._config.tools.get("max_tool_iterations", 10),
            multi_session=self._config.conversation.get("multi_session", True),
            max_history_messages=self._config.conversation.get("max_history_messages"),
            log_level=self._config.logging.get("level", "warning"),
            raw=self._config.raw,
        )

    # ------------------------------------------------------------------
    # Direct access to internal components (for advanced use)
    # ------------------------------------------------------------------

    @property
    def config(self) -> Config:
        """Direct access to the Config object."""
        return self._config

    @property
    def conversation(self) -> ConversationManager:
        """Direct access to the ConversationManager."""
        return self._conversation

    @property
    def tools_registry(self) -> ToolRegistry:
        """Direct access to the ToolRegistry."""
        return self._tools

    @property
    def sync_client(self) -> anthropic.Anthropic:
        """Direct access to the underlying Anthropic sync client."""
        return self._sync_client

    @property
    def async_client(self) -> Optional[anthropic.AsyncAnthropic]:
        """Direct access to the underlying Anthropic async client."""
        return self._async_client

    # ------------------------------------------------------------------
    # Request building — assembles final API kwargs
    # ------------------------------------------------------------------

    def _build_request_kwargs(self, req: SendRequest) -> dict[str, Any]:
        """
        Assemble the full kwargs dict for an API call.
        Applies priority: request > session > config.
        """
        conv = self._conversation

        resolved_model = conv.resolve_param("model", req.model, req.session_id) or "claude-sonnet-4-6"
        resolved_max_tokens = conv.resolve_param("max_tokens", req.max_tokens, req.session_id) or 1024
        resolved_system = req.system or conv.build_system_prompt(req.session_id)
        resolved_temp = conv.resolve_param("temperature", req.temperature, req.session_id)
        resolved_top_p = conv.resolve_param("top_p", req.top_p, req.session_id)
        resolved_top_k = conv.resolve_param("top_k", req.top_k, req.session_id)

        stop_sequences = req.stop_sequences or self._config.model.get("stop_sequences") or []

        # Messages
        prefill = req.prefill or self._config.conversation.get("prefill")
        messages = conv.build_messages(req.session_id, prefill=prefill)

        kwargs: dict[str, Any] = {
            "model": resolved_model,
            "max_tokens": resolved_max_tokens,
            "messages": messages,
        }

        if resolved_system:
            if self._config.system.get("cache_control", False):
                kwargs["system"] = [
                    {
                        "type": "text",
                        "text": resolved_system,
                        "cache_control": {"type": self._config.system.get("cache_control_type", "ephemeral")},
                    }
                ]
            else:
                kwargs["system"] = resolved_system

        if resolved_temp is not None:
            kwargs["temperature"] = float(resolved_temp)
        if resolved_top_p is not None:
            kwargs["top_p"] = float(resolved_top_p)
        if resolved_top_k is not None:
            kwargs["top_k"] = int(resolved_top_k)
        if stop_sequences:
            kwargs["stop_sequences"] = stop_sequences

        service_tier = req.service_tier or self._config.model.get("service_tier")
        if service_tier:
            kwargs["service_tier"] = service_tier

        # Thinking
        thinking_enabled = req.thinking_enabled
        if thinking_enabled is None:
            thinking_enabled = self._config.thinking.get("enabled", False)
        if thinking_enabled:
            budget = req.thinking_budget_tokens or self._config.thinking.get("budget_tokens", 5000)
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}

        # Tools
        tool_names = req.tools  # None = all registered tools
        if self._tools.list_tools():
            kwargs["tools"] = self._tools.to_api_list(tool_names)
            tc = req.tool_choice or self._config.tools.get("tool_choice", "auto")
            kwargs["tool_choice"] = self._tools.build_tool_choice(tc)

        # Metadata
        meta: dict[str, str] = {}
        global_user_id = self._config.metadata.get("user_id")
        if global_user_id:
            meta["user_id"] = str(global_user_id)
        if req.metadata:
            meta.update(req.metadata)
        if meta:
            kwargs["metadata"] = meta

        # Beta headers
        betas = list(req.betas or [])
        betas.extend(self._config.get_active_beta_headers())
        if betas:
            kwargs["betas"] = list(dict.fromkeys(betas))  # deduplicate, preserve order

        # Escape hatch — pass through any raw extra kwargs
        kwargs.update(req.extra_kwargs)

        return kwargs

    # ------------------------------------------------------------------
    # Post-response finalization
    # ------------------------------------------------------------------

    def _finalize_response(self, response: ClaudeResponse, req: SendRequest) -> None:
        """Record history, usage, fire events, handle tool loop."""
        # Record assistant response in history
        self._conversation.add_assistant_message(response.content, req.session_id)

        # Record token usage
        self._conversation.record_usage(response.usage, req.session_id)
        self._bus.emit(EventName.TOKEN_USAGE, response.usage)

        if self._config.logging.get("log_token_usage", True):
            logger.info(
                f"Token usage — input: {response.usage.input_tokens}, "
                f"output: {response.usage.output_tokens}"
            )

        if self._config.logging.get("log_responses", False):
            self._bus.emit(EventName.RAW_RESPONSE, response.raw)

        self._bus.emit(EventName.RESPONSE, response)
        self._bus.emit(EventName.TEXT, response.text)
        if response.has_thinking:
            self._bus.emit(EventName.THINKING, response.thinking)

        self._bus.emit(EventName.REQUEST_END, {"response": response})

        # Auto-run tool loop
        if response.has_tool_calls and self._config.tools.get("auto_run_tools", True):
            self._run_tool_loop_sync(response, req)

        self._conversation.maybe_auto_clear(req.session_id)

    async def _finalize_response_async(self, response: ClaudeResponse, req: SendRequest) -> None:
        self._conversation.add_assistant_message(response.content, req.session_id)
        self._conversation.record_usage(response.usage, req.session_id)
        await self._bus.emit_async(EventName.TOKEN_USAGE, response.usage)
        await self._bus.emit_async(EventName.RESPONSE, response)
        await self._bus.emit_async(EventName.TEXT, response.text)
        if response.has_thinking:
            await self._bus.emit_async(EventName.THINKING, response.thinking)
        await self._bus.emit_async(EventName.REQUEST_END, {"response": response})

        if response.has_tool_calls and self._config.tools.get("auto_run_tools", True):
            await self._run_tool_loop_async(response, req)

        self._conversation.maybe_auto_clear(req.session_id)

    # ------------------------------------------------------------------
    # Tool loop — automatically execute tools and loop back
    # ------------------------------------------------------------------

    def _run_tool_loop_sync(self, response: ClaudeResponse, req: SendRequest) -> ClaudeResponse:
        max_iter = self._config.tools.get("max_tool_iterations", 10)
        iteration = 0

        while response.has_tool_calls and iteration < max_iter:
            iteration += 1
            tool_result_blocks = []

            for tool_call in response.tool_calls:
                try:
                    result = self._tools.execute_sync(tool_call)
                    tool_result_blocks.append(
                        self._tools.result_to_content_block(result)
                    )
                except Exception as e:
                    # Include error as tool result so Claude can respond
                    tool_result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": str(e),
                        "is_error": True,
                    })

            # Add tool results as user message
            self._conversation.add_user_message(tool_result_blocks, req.session_id)
            request_kwargs = self._build_request_kwargs(SendRequest(
                content=tool_result_blocks,
                session_id=req.session_id,
            ))

            use_stream = self._config.streaming.get("enabled", True)
            if use_stream:
                response = self._stream_handler.stream_sync(self._sync_client, request_kwargs)
            else:
                raw = self._sync_client.messages.create(**request_kwargs)
                response = self._stream_handler.parse_non_streaming(raw)

            self._conversation.add_assistant_message(response.content, req.session_id)
            self._conversation.record_usage(response.usage, req.session_id)
            self._bus.emit(EventName.TOKEN_USAGE, response.usage)
            self._bus.emit(EventName.RESPONSE, response)
            self._bus.emit(EventName.TEXT, response.text)

        if response.has_tool_calls and iteration >= max_iter:
            raise MaxToolIterationsError(
                f"Tool loop exceeded max_tool_iterations={max_iter}",
                iterations=iteration,
            )

        return response

    async def _run_tool_loop_async(self, response: ClaudeResponse, req: SendRequest) -> ClaudeResponse:
        max_iter = self._config.tools.get("max_tool_iterations", 10)
        iteration = 0

        while response.has_tool_calls and iteration < max_iter:
            iteration += 1
            tool_result_blocks = []

            for tool_call in response.tool_calls:
                try:
                    result = await self._tools.execute_async(tool_call)
                    tool_result_blocks.append(self._tools.result_to_content_block(result))
                except Exception as e:
                    tool_result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": str(e),
                        "is_error": True,
                    })

            self._conversation.add_user_message(tool_result_blocks, req.session_id)
            request_kwargs = self._build_request_kwargs(SendRequest(
                content=tool_result_blocks,
                session_id=req.session_id,
            ))

            use_stream = self._config.streaming.get("enabled", True)
            if use_stream:
                response = await self._stream_handler.stream_async(self._async_client, request_kwargs)
            else:
                raw = await self._async_client.messages.create(**request_kwargs)
                response = self._stream_handler.parse_non_streaming(raw)

            self._conversation.add_assistant_message(response.content, req.session_id)
            self._conversation.record_usage(response.usage, req.session_id)
            await self._bus.emit_async(EventName.RESPONSE, response)
            await self._bus.emit_async(EventName.TEXT, response.text)

        if response.has_tool_calls and iteration >= max_iter:
            raise MaxToolIterationsError(
                f"Tool loop exceeded max_tool_iterations={max_iter}",
                iterations=iteration,
            )

        return response

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Cleanly shut down ClaudeBox — close HTTP connections and event bus."""
        self._bus.emit(EventName.BOX_CLOSED, self)
        if self._sync_client:
            self._sync_client.close()
        if self._async_client:
            # Schedule async close
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self._async_client.close())
                else:
                    loop.run_until_complete(self._async_client.close())
            except Exception:
                pass
        self._bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        return (
            f"ClaudeBox("
            f"model={self._config.model.get('model')!r}, "
            f"sessions={len(self._conversation.list_sessions())}, "
            f"tools={len(self._tools.list_tools())})"
        )
