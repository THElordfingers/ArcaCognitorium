"""
claudebox.streaming
===================
Unified streaming handler for sync, async, and threaded contexts.

Normalizes the Anthropic SDK's streaming interface into a consistent
output regardless of the calling context. Fires events as tokens arrive.
"""

from __future__ import annotations

import asyncio
import logging
import queue
import threading
from typing import AsyncIterator, Callable, Iterator, Optional

import anthropic

from .config import Config
from .events import EventBus, EventName
from .exceptions import StreamInterruptedError, wrap_anthropic_error
from .models import (
    ClaudeResponse,
    ContentBlock,
    ImageBlock,
    StreamComplete,
    StreamEvent,
    StreamEventType,
    StreamThinkingToken,
    StreamToken,
    TextBlock,
    ThinkingBlock,
    TokenUsage,
    ToolUseBlock,
    RedactedThinkingBlock,
)

logger = logging.getLogger("claudebox.streaming")


def _parse_response(raw) -> ClaudeResponse:
    """Convert a raw anthropic Message object into a ClaudeResponse."""
    from .models import Role, StopReason

    content_blocks: list[ContentBlock] = []
    for block in (raw.content or []):
        btype = getattr(block, "type", None)
        if btype == "text":
            content_blocks.append(TextBlock(text=block.text))
        elif btype == "image":
            from .models import ImageSource
            src = block.source
            content_blocks.append(ImageBlock(
                source=ImageSource(
                    type=src.type,
                    media_type=getattr(src, "media_type", None),
                    data=getattr(src, "data", None),
                    url=getattr(src, "url", None),
                )
            ))
        elif btype == "tool_use":
            content_blocks.append(ToolUseBlock(
                id=block.id,
                name=block.name,
                input=dict(block.input),
            ))
        elif btype == "thinking":
            content_blocks.append(ThinkingBlock(thinking=block.thinking))
        elif btype == "redacted_thinking":
            content_blocks.append(RedactedThinkingBlock(data=block.data))
        else:
            # Unknown block type — wrap as TextBlock with raw string
            content_blocks.append(TextBlock(text=str(block)))

    usage_raw = getattr(raw, "usage", None)
    usage = TokenUsage(
        input_tokens=getattr(usage_raw, "input_tokens", 0),
        output_tokens=getattr(usage_raw, "output_tokens", 0),
        cache_creation_input_tokens=getattr(usage_raw, "cache_creation_input_tokens", 0),
        cache_read_input_tokens=getattr(usage_raw, "cache_read_input_tokens", 0),
    ) if usage_raw else TokenUsage()

    stop_reason_raw = getattr(raw, "stop_reason", None)
    try:
        stop_reason = StopReason(stop_reason_raw) if stop_reason_raw else None
    except ValueError:
        stop_reason = None

    return ClaudeResponse(
        id=raw.id,
        model=raw.model,
        role=getattr(raw, "role", "assistant"),
        content=content_blocks,
        stop_reason=stop_reason,
        stop_sequence=getattr(raw, "stop_sequence", None),
        usage=usage,
        request_id=getattr(raw, "_request_id", None),
        raw=raw,
    )


class StreamHandler:
    """
    Handles a single streaming API call.

    Fires token events as they arrive and assembles the final ClaudeResponse.
    Works in sync, async, and threaded-GUI contexts.
    """

    def __init__(self, config: Config, bus: EventBus):
        self._config = config
        self._bus = bus

    # ------------------------------------------------------------------
    # Sync streaming
    # ------------------------------------------------------------------

    def stream_sync(
        self,
        client: anthropic.Anthropic,
        request_kwargs: dict,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> ClaudeResponse:
        """
        Execute a streaming request synchronously.

        Fires bus events for every token. Also calls on_token callback if provided
        (convenience for callers that don't want to set up full event subscriptions).

        Returns the fully assembled ClaudeResponse when complete.
        """
        yield_raw = self._config.streaming.get("yield_raw_events", False)
        stream_thinking = self._config.thinking.get("stream_thinking", True)

        self._bus.emit(EventName.STREAM_START, None)

        try:
            with client.messages.stream(**request_kwargs) as stream:
                for event in stream:
                    if yield_raw:
                        self._emit_raw_event(event)

                    # Text tokens
                    if hasattr(event, "type"):
                        etype = getattr(event, "type", "")

                        if etype == "content_block_delta":
                            delta = getattr(event, "delta", None)
                            if delta is None:
                                continue
                            dtype = getattr(delta, "type", "")

                            if dtype == "text_delta":
                                text = getattr(delta, "text", "")
                                if text:
                                    token = StreamToken(text=text, index=getattr(event, "index", 0))
                                    self._bus.emit(EventName.TOKEN, token)
                                    if on_token:
                                        on_token(text)

                            elif dtype == "thinking_delta" and stream_thinking:
                                thinking = getattr(delta, "thinking", "")
                                if thinking:
                                    token = StreamThinkingToken(thinking=thinking, index=getattr(event, "index", 0))
                                    self._bus.emit(EventName.THINKING_TOKEN, token)

                final_message = stream.get_final_message()

            response = _parse_response(final_message)
            complete = StreamComplete(response=response)
            self._bus.emit(EventName.STREAM_END, complete)
            return response

        except anthropic.APIError as e:
            wrapped = wrap_anthropic_error(e)
            self._bus.emit(EventName.STREAM_ERROR, wrapped)
            self._bus.emit(EventName.API_ERROR, wrapped)
            raise wrapped
        except Exception as e:
            err = StreamInterruptedError(str(e), cause=e)
            self._bus.emit(EventName.STREAM_ERROR, err)
            raise err

    # ------------------------------------------------------------------
    # Async streaming
    # ------------------------------------------------------------------

    async def stream_async(
        self,
        client: anthropic.AsyncAnthropic,
        request_kwargs: dict,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> ClaudeResponse:
        """
        Execute a streaming request asynchronously.
        """
        yield_raw = self._config.streaming.get("yield_raw_events", False)
        stream_thinking = self._config.thinking.get("stream_thinking", True)

        await self._bus.emit_async(EventName.STREAM_START, None)

        try:
            async with client.messages.stream(**request_kwargs) as stream:
                async for event in stream:
                    if yield_raw:
                        self._emit_raw_event(event)

                    if hasattr(event, "type"):
                        etype = getattr(event, "type", "")

                        if etype == "content_block_delta":
                            delta = getattr(event, "delta", None)
                            if delta is None:
                                continue
                            dtype = getattr(delta, "type", "")

                            if dtype == "text_delta":
                                text = getattr(delta, "text", "")
                                if text:
                                    token = StreamToken(text=text, index=getattr(event, "index", 0))
                                    await self._bus.emit_async(EventName.TOKEN, token)
                                    if on_token:
                                        on_token(text)

                            elif dtype == "thinking_delta" and stream_thinking:
                                thinking = getattr(delta, "thinking", "")
                                if thinking:
                                    token = StreamThinkingToken(thinking=thinking, index=getattr(event, "index", 0))
                                    await self._bus.emit_async(EventName.THINKING_TOKEN, token)

                final_message = await stream.get_final_message()

            response = _parse_response(final_message)
            complete = StreamComplete(response=response)
            await self._bus.emit_async(EventName.STREAM_END, complete)
            return response

        except anthropic.APIError as e:
            wrapped = wrap_anthropic_error(e)
            await self._bus.emit_async(EventName.STREAM_ERROR, wrapped)
            await self._bus.emit_async(EventName.API_ERROR, wrapped)
            raise wrapped
        except Exception as e:
            err = StreamInterruptedError(str(e), cause=e)
            await self._bus.emit_async(EventName.STREAM_ERROR, err)
            raise err

    # ------------------------------------------------------------------
    # Threaded streaming (for GUI frameworks like Tkinter / PyQt)
    # Runs the stream in a background thread, delivers tokens via queue
    # ------------------------------------------------------------------

    def stream_threaded(
        self,
        client: anthropic.Anthropic,
        request_kwargs: dict,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[ClaudeResponse], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> threading.Thread:
        """
        Execute a streaming request in a background thread.

        Returns the thread immediately — streaming happens in the background.
        Use on_token, on_complete, on_error callbacks (or bus events) to receive output.

        Safe to call from GUI main threads — callbacks are not automatically
        marshalled to the GUI thread (caller is responsible for that if needed,
        e.g. widget.after(0, callback) in Tkinter or QMetaObject.invokeMethod in Qt).
        """
        def _run():
            try:
                response = self.stream_sync(client, request_kwargs, on_token=on_token)
                if on_complete:
                    on_complete(response)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    logger.error(f"Threaded stream error: {e}", exc_info=e)

        thread = threading.Thread(target=_run, daemon=True, name="claudebox-stream")
        thread.start()
        return thread

    # ------------------------------------------------------------------
    # Generator interfaces (sync and async) for callers that want to
    # iterate over tokens themselves rather than using callbacks/events
    # ------------------------------------------------------------------

    def token_generator(
        self,
        client: anthropic.Anthropic,
        request_kwargs: dict,
    ) -> Iterator[str]:
        """
        Sync generator that yields text tokens one at a time.

        Usage:
            for token in box.token_generator(request):
                print(token, end="", flush=True)
        """
        yield_raw = self._config.streaming.get("yield_raw_events", False)

        self._bus.emit(EventName.STREAM_START, None)
        try:
            with client.messages.stream(**request_kwargs) as stream:
                for event in stream:
                    if yield_raw:
                        self._emit_raw_event(event)
                    if getattr(event, "type", "") == "content_block_delta":
                        delta = getattr(event, "delta", None)
                        if delta and getattr(delta, "type", "") == "text_delta":
                            text = getattr(delta, "text", "")
                            if text:
                                self._bus.emit(EventName.TOKEN, StreamToken(text=text))
                                yield text

                final_message = stream.get_final_message()

            response = _parse_response(final_message)
            self._bus.emit(EventName.STREAM_END, StreamComplete(response=response))

        except anthropic.APIError as e:
            wrapped = wrap_anthropic_error(e)
            self._bus.emit(EventName.STREAM_ERROR, wrapped)
            raise wrapped

    async def token_generator_async(
        self,
        client: anthropic.AsyncAnthropic,
        request_kwargs: dict,
    ) -> AsyncIterator[str]:
        """
        Async generator that yields text tokens one at a time.

        Usage:
            async for token in box.token_generator_async(request):
                print(token, end="", flush=True)
        """
        yield_raw = self._config.streaming.get("yield_raw_events", False)

        await self._bus.emit_async(EventName.STREAM_START, None)
        try:
            async with client.messages.stream(**request_kwargs) as stream:
                async for event in stream:
                    if yield_raw:
                        self._emit_raw_event(event)
                    if getattr(event, "type", "") == "content_block_delta":
                        delta = getattr(event, "delta", None)
                        if delta and getattr(delta, "type", "") == "text_delta":
                            text = getattr(delta, "text", "")
                            if text:
                                await self._bus.emit_async(EventName.TOKEN, StreamToken(text=text))
                                yield text

                final_message = await stream.get_final_message()

            response = _parse_response(final_message)
            await self._bus.emit_async(EventName.STREAM_END, StreamComplete(response=response))

        except anthropic.APIError as e:
            wrapped = wrap_anthropic_error(e)
            await self._bus.emit_async(EventName.STREAM_ERROR, wrapped)
            raise wrapped

    # ------------------------------------------------------------------
    # Non-streaming response parser (for when streaming is disabled)
    # ------------------------------------------------------------------

    def parse_non_streaming(self, raw_response) -> ClaudeResponse:
        """Convert a non-streaming API response into a ClaudeResponse."""
        return _parse_response(raw_response)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _emit_raw_event(self, event) -> None:
        try:
            etype_str = getattr(event, "type", "unknown")
            try:
                etype = StreamEventType(etype_str)
            except ValueError:
                etype = StreamEventType.PING
            self._bus.emit(EventName.STREAM_EVENT, StreamEvent(type=etype, data=event))
        except Exception:
            pass  # Never let raw event emission crash the stream
