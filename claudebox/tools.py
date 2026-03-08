"""
claudebox.tools
===============
Tool registry, schema extraction, validation, and execution.

Tools can be registered as plain Python functions (sync or async).
Schema is auto-extracted from type hints and docstrings, or provided manually.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import threading
import time
from typing import Any, Callable, Optional, Union

from .config import Config
from .events import EventBus, EventName
from .exceptions import (
    MaxToolIterationsError,
    ToolAlreadyRegisteredError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolTimeoutError,
    ToolValidationError,
)
from .models import ToolCall, ToolDefinition, ToolResult

logger = logging.getLogger("claudebox.tools")


class ToolRegistry:
    """
    Registry for all tools available to Claude.

    Supports decorator registration, explicit registration, and
    manual schema definition. Handles sync and async tools.
    """

    def __init__(self, config: Config, bus: EventBus):
        self._config = config
        self._bus = bus
        self._tools: dict[str, ToolDefinition] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        fn: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Union[Callable, "ToolRegistry"]:
        """
        Register a tool function.

        Can be used as a decorator or called directly:

            # Decorator
            @box.tool
            def get_weather(location: str) -> str:
                ...

            # Decorator with options
            @box.tool(name="weather", description="Get weather", timeout=10.0)
            def get_weather(location: str) -> str:
                ...

            # Direct registration
            box.register_tool(get_weather)
            box.register_tool(get_weather, name="weather", description="Get weather")
        """
        def _register(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_description = description or _extract_docstring_description(func)
            tool_schema = schema or _extract_schema(func)
            tool_timeout = timeout or self._config.tools.get("default_tool_timeout", 30.0)
            is_async = asyncio.iscoroutinefunction(func)

            with self._lock:
                if tool_name in self._tools:
                    raise ToolAlreadyRegisteredError(
                        f"Tool '{tool_name}' is already registered. "
                        f"Use unregister('{tool_name}') first.",
                        tool_name=tool_name,
                    )

                self._tools[tool_name] = ToolDefinition(
                    name=tool_name,
                    description=tool_description,
                    input_schema=tool_schema,
                    callable=func,
                    is_async=is_async,
                    timeout=tool_timeout,
                )

            self._bus.emit(EventName.TOOL_REGISTERED, tool_name)
            logger.debug(f"Tool registered: '{tool_name}' ({'async' if is_async else 'sync'})")
            return func

        if fn is not None:
            # Called as @box.tool (no arguments)
            return _register(fn)
        else:
            # Called as @box.tool(...) or box.tool(name=...) — return decorator
            return _register

    # Alias
    def register_tool(
        self,
        fn: Callable,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Explicitly register a tool function (non-decorator form)."""
        self.register(fn, name=name, description=description, schema=schema, timeout=timeout)

    def unregister(self, name: str) -> None:
        """Remove a tool from the registry."""
        with self._lock:
            if name not in self._tools:
                raise ToolNotFoundError(f"Tool '{name}' is not registered.", tool_name=name)
            del self._tools[name]
        self._bus.emit(EventName.TOOL_UNREGISTERED, name)
        logger.debug(f"Tool unregistered: '{name}'")

    def unregister_all(self) -> None:
        """Remove all tools from the registry."""
        with self._lock:
            names = list(self._tools.keys())
            self._tools.clear()
        for name in names:
            self._bus.emit(EventName.TOOL_UNREGISTERED, name)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get(self, name: str) -> ToolDefinition:
        with self._lock:
            tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.", tool_name=name)
        return tool

    def has(self, name: str) -> bool:
        with self._lock:
            return name in self._tools

    def list_tools(self) -> list[str]:
        with self._lock:
            return list(self._tools.keys())

    def list_definitions(self) -> list[ToolDefinition]:
        with self._lock:
            return list(self._tools.values())

    def to_api_list(self, tool_names: Optional[list[str]] = None) -> list[dict]:
        """
        Return tools in API format (list of dicts with name/description/input_schema).

        If tool_names is provided, only include those tools.
        If None, include all registered tools.
        """
        with self._lock:
            if tool_names is None:
                tools = list(self._tools.values())
            else:
                tools = []
                for name in tool_names:
                    if name in self._tools:
                        tools.append(self._tools[name])
                    else:
                        raise ToolNotFoundError(
                            f"Tool '{name}' is not registered.",
                            tool_name=name,
                        )
        return [t.to_api_dict() for t in tools]

    def build_tool_choice(self, tool_choice: Optional[str] = None) -> Optional[dict]:
        """Convert a tool_choice string to the API dict format."""
        choice = tool_choice or self._config.tools.get("tool_choice", "auto")

        if choice == "auto":
            return {"type": "auto"}
        if choice == "any":
            return {"type": "any"}
        if choice == "none":
            return {"type": "none"}
        # Specific tool name
        return {"type": "tool", "name": choice}

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_sync(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call synchronously.

        Validates inputs, runs the function, wraps the result.
        """
        tool = self.get(tool_call.name)
        start = time.monotonic()

        logger.debug(f"Executing tool '{tool_call.name}' with input: {tool_call.input}")
        self._bus.emit(EventName.TOOL_CALL, tool_call)

        if self._config.tools.get("validate_tool_inputs", True):
            self._validate_inputs(tool, tool_call.input)

        try:
            if tool.is_async:
                # Run async tool from sync context
                output = _run_async_in_sync(tool.callable(**tool_call.input))
            else:
                if tool.timeout:
                    output = _run_with_timeout(tool.callable, tool_call.input, tool.timeout, tool_call.name)
                else:
                    output = tool.callable(**tool_call.input)

            elapsed_ms = (time.monotonic() - start) * 1000

            # Normalize output to string
            if not isinstance(output, str):
                try:
                    output = json.dumps(output)
                except (TypeError, ValueError):
                    output = str(output)

            result = ToolResult(
                tool_use_id=tool_call.id,
                tool_name=tool_call.name,
                output=output,
                is_error=False,
                execution_time_ms=elapsed_ms,
            )
            self._bus.emit(EventName.TOOL_RESULT, result)

            if self._config.logging.get("log_tool_calls", True):
                logger.info(f"Tool '{tool_call.name}' completed in {elapsed_ms:.1f}ms")

            return result

        except ToolTimeoutError:
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            err_msg = f"Tool '{tool_call.name}' raised {type(e).__name__}: {e}"
            logger.error(err_msg, exc_info=e)

            result = ToolResult(
                tool_use_id=tool_call.id,
                tool_name=tool_call.name,
                output=err_msg,
                is_error=True,
                execution_time_ms=elapsed_ms,
            )
            self._bus.emit(EventName.TOOL_RESULT, result)
            self._bus.emit(EventName.TOOL_ERROR, {"tool_call": tool_call, "error": e})

            raise ToolExecutionError(err_msg, tool_name=tool_call.name, cause=e)

    async def execute_async(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call asynchronously."""
        tool = self.get(tool_call.name)
        start = time.monotonic()

        logger.debug(f"Executing tool '{tool_call.name}' async with input: {tool_call.input}")
        await self._bus.emit_async(EventName.TOOL_CALL, tool_call)

        if self._config.tools.get("validate_tool_inputs", True):
            self._validate_inputs(tool, tool_call.input)

        try:
            if tool.is_async:
                if tool.timeout:
                    output = await asyncio.wait_for(
                        tool.callable(**tool_call.input),
                        timeout=tool.timeout,
                    )
                else:
                    output = await tool.callable(**tool_call.input)
            else:
                # Run sync tool in executor to avoid blocking event loop
                loop = asyncio.get_event_loop()
                if tool.timeout:
                    output = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: tool.callable(**tool_call.input)),
                        timeout=tool.timeout,
                    )
                else:
                    output = await loop.run_in_executor(None, lambda: tool.callable(**tool_call.input))

            elapsed_ms = (time.monotonic() - start) * 1000

            if not isinstance(output, str):
                try:
                    output = json.dumps(output)
                except (TypeError, ValueError):
                    output = str(output)

            result = ToolResult(
                tool_use_id=tool_call.id,
                tool_name=tool_call.name,
                output=output,
                is_error=False,
                execution_time_ms=elapsed_ms,
            )
            await self._bus.emit_async(EventName.TOOL_RESULT, result)
            return result

        except asyncio.TimeoutError:
            timeout_err = ToolTimeoutError(
                f"Tool '{tool_call.name}' timed out after {tool.timeout}s",
                tool_name=tool_call.name,
                timeout=tool.timeout,
            )
            await self._bus.emit_async(EventName.TOOL_ERROR, {"tool_call": tool_call, "error": timeout_err})
            raise timeout_err

        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            err_msg = f"Tool '{tool_call.name}' raised {type(e).__name__}: {e}"

            result = ToolResult(
                tool_use_id=tool_call.id,
                tool_name=tool_call.name,
                output=err_msg,
                is_error=True,
                execution_time_ms=elapsed_ms,
            )
            await self._bus.emit_async(EventName.TOOL_RESULT, result)
            await self._bus.emit_async(EventName.TOOL_ERROR, {"tool_call": tool_call, "error": e})
            raise ToolExecutionError(err_msg, tool_name=tool_call.name, cause=e)

    # ------------------------------------------------------------------
    # Tool result -> API message block
    # ------------------------------------------------------------------

    def result_to_content_block(self, result: ToolResult) -> dict:
        """Convert a ToolResult to an API-format tool_result content block."""
        return {
            "type": "tool_result",
            "tool_use_id": result.tool_use_id,
            "content": result.output,
            "is_error": result.is_error,
        }

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def _validate_inputs(self, tool: ToolDefinition, inputs: dict[str, Any]) -> None:
        """Basic schema validation against required fields."""
        schema = tool.input_schema
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        errors = []

        for field in required:
            if field not in inputs:
                errors.append(f"Missing required field: '{field}'")

        for field, value in inputs.items():
            if field not in properties:
                # Unknown field — warn but don't error
                logger.debug(f"Tool '{tool.name}' received unexpected input field: '{field}'")

        if errors:
            raise ToolValidationError(
                f"Tool '{tool.name}' input validation failed: {'; '.join(errors)}",
                tool_name=tool.name,
                validation_errors=errors,
            )

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        with self._lock:
            count = len(self._tools)
        return f"ToolRegistry(tools={count}: {self.list_tools()})"


# ---------------------------------------------------------------------------
# Schema extraction from Python functions
# ---------------------------------------------------------------------------

def _extract_docstring_description(fn: Callable) -> str:
    """Extract the first line of a function's docstring as description."""
    doc = inspect.getdoc(fn)
    if not doc:
        return f"Execute {fn.__name__}"
    # First non-empty line
    for line in doc.splitlines():
        line = line.strip()
        if line:
            return line
    return fn.__name__


def _extract_schema(fn: Callable) -> dict[str, Any]:
    """
    Auto-extract a JSON Schema from a function's type hints and docstring.

    Supports: str, int, float, bool, list, dict, Optional[T], and Literal[...].
    Falls back to {"type": "string"} for unknown types.
    """
    sig = inspect.signature(fn)
    hints = {}
    try:
        hints = inspect.get_annotations(fn) if hasattr(inspect, "get_annotations") else fn.__annotations__
    except Exception:
        pass

    properties: dict[str, Any] = {}
    required: list[str] = []

    # Parse docstring for per-param descriptions (Args: section)
    param_docs = _parse_param_docs(fn)

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        hint = hints.get(param_name)
        prop = _hint_to_json_schema(hint)

        if param_name in param_docs:
            prop["description"] = param_docs[param_name]

        properties[param_name] = prop

        # Required if no default
        if param.default is inspect.Parameter.empty:
            # Check if Optional (has default of None implicitly)
            if not _is_optional(hint):
                required.append(param_name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _hint_to_json_schema(hint: Any) -> dict[str, Any]:
    """Convert a Python type hint to a JSON Schema property dict."""
    if hint is None:
        return {"type": "string"}

    # Handle string annotations
    if isinstance(hint, str):
        return {"type": "string"}

    origin = getattr(hint, "__origin__", None)
    args = getattr(hint, "__args__", ())

    # Optional[T] = Union[T, None]
    if origin is Union or str(origin) == "typing.Union":
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _hint_to_json_schema(non_none[0])
        return {"type": "string"}

    # List[T]
    if origin is list or origin is List:
        item_schema = _hint_to_json_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema}

    # Dict
    if origin is dict or origin is Dict:
        return {"type": "object"}

    # Literal["a", "b"]
    if origin is Literal or str(origin) == "typing.Literal":
        return {"type": "string", "enum": list(args)}

    # Primitives
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return {"type": type_map.get(hint, "string")}


def _is_optional(hint: Any) -> bool:
    """Return True if hint is Optional[T] (i.e. Union[T, None])."""
    origin = getattr(hint, "__origin__", None)
    if origin is Union or str(origin) == "typing.Union":
        return type(None) in getattr(hint, "__args__", ())
    return False


def _parse_param_docs(fn: Callable) -> dict[str, str]:
    """Parse Args section of a Google-style or NumPy-style docstring."""
    doc = inspect.getdoc(fn) or ""
    params: dict[str, str] = {}
    in_args = False
    current_param = None
    current_desc: list[str] = []

    for line in doc.splitlines():
        stripped = line.strip()

        if stripped.lower() in ("args:", "arguments:", "parameters:", "params:"):
            in_args = True
            continue

        if in_args:
            # Section end
            if stripped and not line.startswith(" ") and not line.startswith("\t") and stripped.endswith(":"):
                if current_param:
                    params[current_param] = " ".join(current_desc).strip()
                in_args = False
                continue

            # New param line: "    param_name: description" or "    param_name (type): desc"
            if stripped and (line.startswith("    ") or line.startswith("\t")):
                colon_idx = stripped.find(":")
                if colon_idx > 0:
                    possible_name = stripped[:colon_idx].strip()
                    # Strip type annotation in parens
                    paren_idx = possible_name.find("(")
                    if paren_idx > 0:
                        possible_name = possible_name[:paren_idx].strip()
                    if possible_name.isidentifier():
                        if current_param:
                            params[current_param] = " ".join(current_desc).strip()
                        current_param = possible_name
                        current_desc = [stripped[colon_idx + 1:].strip()]
                        continue

            # Continuation of current param
            if current_param and stripped:
                current_desc.append(stripped)

    if current_param:
        params[current_param] = " ".join(current_desc).strip()

    return params


# ---------------------------------------------------------------------------
# Execution utilities
# ---------------------------------------------------------------------------

def _run_with_timeout(fn: Callable, kwargs: dict, timeout: float, tool_name: str) -> Any:
    """Run a sync function with a timeout using a thread."""
    result_container: list = [None]
    error_container: list = [None]

    def _target():
        try:
            result_container[0] = fn(**kwargs)
        except Exception as e:
            error_container[0] = e

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise ToolTimeoutError(
            f"Tool '{tool_name}' timed out after {timeout}s",
            tool_name=tool_name,
            timeout=timeout,
        )

    if error_container[0] is not None:
        raise error_container[0]

    return result_container[0]


def _run_async_in_sync(coro) -> Any:
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# Imports needed for type hint parsing
from typing import Union, List, Dict, Literal
