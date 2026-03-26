"""
claudebox.config
================
Config file loader, validator, and live accessor.

Reads claudebox.config.yaml, validates every field, provides typed access
to every option, and supports hot-reload at runtime.

The config is a singleton within a ClaudeBox instance — one box, one config.
Multiple boxes can have different configs pointing at different files.
"""

from __future__ import annotations

import copy
import logging
import os
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")

from .exceptions import ConfigNotFoundError, ConfigParseError, ConfigValidationError

logger = logging.getLogger("claudebox.config")

# Default config file name searched for relative to cwd and package root
DEFAULT_CONFIG_FILENAME = "claudebox.config.yaml"

# Canonical list of all valid fields per section — used for unknown-key warnings
_KNOWN_SECTIONS = {
    "api", "keyring", "connection", "model", "system", "thinking",
    "conversation", "streaming", "tools", "vision", "files", "batches",
    "events", "cache", "beta", "metadata", "logging", "platform",
}


class Config:
    """
    Loaded, validated, and live-accessible configuration for a ClaudeBox instance.

    Access pattern:
        cfg = Config.load("/path/to/claudebox.config.yaml")
        cfg.model.model          -> "claude-sonnet-4-6"
        cfg.connection.timeout_total -> 600.0
        cfg.raw                  -> full raw dict

    Hot-reload:
        cfg.reload()             -> re-reads and re-validates the file in place
    """

    def __init__(self, data: dict[str, Any], source_path: Optional[Path] = None):
        self._data = data
        self._source_path = source_path
        self._build_sections()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> "Config":
        """
        Load config from a YAML file.

        Search order when path is None:
          1. ./claudebox.config.yaml  (current working directory)
          2. ~/claudebox.config.yaml  (home directory)
          3. Built-in defaults only   (no file required)
        """
        if path is not None:
            resolved = Path(path).expanduser().resolve()
            if not resolved.exists():
                raise ConfigNotFoundError(
                    f"Config file not found: {resolved}",
                    context={"path": str(resolved)},
                )
            return cls._load_file(resolved)

        # Auto-search
        candidates = [
            Path.cwd() / DEFAULT_CONFIG_FILENAME,
            Path.home() / DEFAULT_CONFIG_FILENAME,
        ]
        for candidate in candidates:
            if candidate.exists():
                return cls._load_file(candidate)

        # No file found — use pure defaults
        logger.debug("No config file found — using built-in defaults")
        return cls(_deep_merge(_DEFAULTS, {}))

    @classmethod
    def _load_file(cls, path: Path) -> "Config":
        logger.debug(f"Loading config from {path}")
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            raise ConfigNotFoundError(f"Could not read config file: {path}", cause=e)

        try:
            raw = yaml.safe_load(text) or {}
        except yaml.YAMLError as e:
            raise ConfigParseError(f"Failed to parse config file: {path}\n{e}", cause=e)

        if not isinstance(raw, dict):
            raise ConfigParseError(f"Config file must be a YAML mapping, got {type(raw).__name__}")

        # Warn on unknown top-level sections
        for key in raw:
            if key not in _KNOWN_SECTIONS:
                logger.warning(f"Unknown config section '{key}' — ignoring")

        # Merge with defaults (file values override defaults)
        merged = _deep_merge(_DEFAULTS, raw)
        instance = cls(merged, source_path=path)
        instance._validate()
        return instance

    def reload(self) -> None:
        """Re-read and re-validate the source config file in place."""
        if self._source_path is None:
            logger.warning("No source path — nothing to reload")
            return
        reloaded = self._load_file(self._source_path)
        self._data = reloaded._data
        self._build_sections()
        logger.info(f"Config reloaded from {self._source_path}")

    # ------------------------------------------------------------------
    # Section accessors — each returns a _Section view of that subtree
    # ------------------------------------------------------------------

    def _build_sections(self) -> None:
        self.api = _Section(self._data.get("api", {}))
        self.keyring = _Section(self._data.get("keyring", {}))
        self.connection = _Section(self._data.get("connection", {}))
        self.model = _Section(self._data.get("model", {}))
        self.system = _Section(self._data.get("system", {}))
        self.thinking = _Section(self._data.get("thinking", {}))
        self.conversation = _Section(self._data.get("conversation", {}))
        self.streaming = _Section(self._data.get("streaming", {}))
        self.tools = _Section(self._data.get("tools", {}))
        self.vision = _Section(self._data.get("vision", {}))
        self.files = _Section(self._data.get("files", {}))
        self.batches = _Section(self._data.get("batches", {}))
        self.events = _Section(self._data.get("events", {}))
        self.cache = _Section(self._data.get("cache", {}))
        self.beta = _Section(self._data.get("beta", {}))
        self.metadata = _Section(self._data.get("metadata", {}))
        self.logging = _Section(self._data.get("logging", {}))
        self.platform = _Section(self._data.get("platform", {}))

    @property
    def raw(self) -> dict[str, Any]:
        """Full raw config dict — a deep copy so callers can't mutate internal state."""
        return copy.deepcopy(self._data)

    @property
    def source_path(self) -> Optional[Path]:
        return self._source_path

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_api_key(self) -> Optional[str]:
        """
        Resolve the API key using the configured source.
        Priority: direct value > env var > keyring
        """
        direct = self.api.get("api_key")
        if direct:
            return str(direct)

        source = self.api.get("api_key_source", "env")

        if source == "env":
            env_var = self.api.get("api_key_env_var", "CLAUDE_API_KEY")
            return os.environ.get(env_var)

        if source == "keyring":
            try:
                import keyring as _keyring
                service = self.keyring.get("service_name", "claudebox")
                username = self.keyring.get("username", "claude_api_key")
                return _keyring.get_password(service, username)
            except ImportError:
                raise ConfigValidationError(
                    "api_key_source is 'keyring' but keyring package is not installed. "
                    "Run: pip install keyring",
                    field="api.api_key_source",
                )

        return None

    def get_active_beta_headers(self) -> list[str]:
        """Return all beta header strings that are currently enabled."""
        headers = []
        beta = self._data.get("beta", {})
        header_map = {
            "interleaved_thinking": "interleaved_thinking_header",
            "code_execution": "code_execution_header",
            "files_api": "files_api_header",
            "mcp_connector": "mcp_connector_header",
            "extended_output": "extended_output_header",
            "computer_use": "computer_use_header",
            "token_counting": "token_counting_header",
            "prompt_caching": "prompt_caching_header",
            "message_batches": "message_batches_header",
            "fine_tuning": "fine_tuning_header",
        }
        for flag, header_key in header_map.items():
            if beta.get(flag, False):
                header_val = beta.get(header_key)
                if header_val:
                    headers.append(header_val)

        # Extra arbitrary headers
        extras = beta.get("extra_beta_headers", [])
        if isinstance(extras, list):
            headers.extend(extras)

        return headers

    def get_platform(self) -> str:
        return self._data.get("platform", {}).get("provider", "anthropic")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        self._validate_model()
        self._validate_connection()
        self._validate_thinking()
        self._validate_tools()
        self._validate_logging()
        self._validate_streaming()
        self._validate_batches()

    def _validate_model(self) -> None:
        m = self._data.get("model", {})
        max_tokens = m.get("max_tokens", 1024)
        if not isinstance(max_tokens, int) or max_tokens < 1:
            raise ConfigValidationError(
                f"model.max_tokens must be a positive integer, got {max_tokens!r}",
                field="model.max_tokens", value=max_tokens,
            )
        temp = m.get("temperature")
        if temp is not None and not (0.0 <= float(temp) <= 1.0):
            raise ConfigValidationError(
                f"model.temperature must be between 0.0 and 1.0, got {temp!r}",
                field="model.temperature", value=temp,
            )
        top_p = m.get("top_p")
        if top_p is not None and not (0.0 <= float(top_p) <= 1.0):
            raise ConfigValidationError(
                f"model.top_p must be between 0.0 and 1.0, got {top_p!r}",
                field="model.top_p", value=top_p,
            )
        top_k = m.get("top_k")
        if top_k is not None and (not isinstance(top_k, int) or top_k < 1):
            raise ConfigValidationError(
                f"model.top_k must be a positive integer, got {top_k!r}",
                field="model.top_k", value=top_k,
            )

    def _validate_connection(self) -> None:
        c = self._data.get("connection", {})
        retries = c.get("max_retries", 2)
        if not isinstance(retries, int) or retries < 0:
            raise ConfigValidationError(
                f"connection.max_retries must be a non-negative integer, got {retries!r}",
                field="connection.max_retries", value=retries,
            )

    def _validate_thinking(self) -> None:
        t = self._data.get("thinking", {})
        if t.get("enabled", False):
            budget = t.get("budget_tokens")
            if budget is not None and (not isinstance(budget, int) or budget < 1024):
                raise ConfigValidationError(
                    f"thinking.budget_tokens must be >= 1024 when thinking is enabled, got {budget!r}",
                    field="thinking.budget_tokens", value=budget,
                )

    def _validate_tools(self) -> None:
        t = self._data.get("tools", {})
        choice = t.get("tool_choice", "auto")
        valid_choices = {"auto", "any", "none"}
        # Also allow arbitrary string (specific tool name)
        if not isinstance(choice, str):
            raise ConfigValidationError(
                f"tools.tool_choice must be a string, got {choice!r}",
                field="tools.tool_choice", value=choice,
            )
        max_iter = t.get("max_tool_iterations", 10)
        if not isinstance(max_iter, int) or max_iter < 1:
            raise ConfigValidationError(
                f"tools.max_tool_iterations must be a positive integer, got {max_iter!r}",
                field="tools.max_tool_iterations", value=max_iter,
            )

    def _validate_logging(self) -> None:
        l = self._data.get("logging", {})
        valid_levels = {"debug", "info", "warning", "error", "critical", "off"}
        level = l.get("level", "warning").lower()
        if level not in valid_levels:
            raise ConfigValidationError(
                f"logging.level must be one of {valid_levels}, got {level!r}",
                field="logging.level", value=level,
            )

    def _validate_streaming(self) -> None:
        s = self._data.get("streaming", {})
        valid_modes = {"direct", "threaded"}
        mode = s.get("thread_mode", "direct")
        if mode not in valid_modes:
            raise ConfigValidationError(
                f"streaming.thread_mode must be one of {valid_modes}, got {mode!r}",
                field="streaming.thread_mode", value=mode,
            )

    def _validate_batches(self) -> None:
        b = self._data.get("batches", {})
        interval = b.get("poll_interval_seconds", 60)
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise ConfigValidationError(
                f"batches.poll_interval_seconds must be a positive number, got {interval!r}",
                field="batches.poll_interval_seconds", value=interval,
            )

    def __repr__(self) -> str:
        src = str(self._source_path) if self._source_path else "<defaults>"
        return f"Config(source={src!r}, model={self.model.get('model')!r})"


# ------------------------------------------------------------------
# Section — dict-backed attribute-style access
# ------------------------------------------------------------------

class _Section:
    """Provides both dict-style and attribute-style access to a config subtree."""

    def __init__(self, data: dict[str, Any]):
        object.__setattr__(self, "_data", data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"Config has no option '{key}'")

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"_Section({self._data!r})"

    def as_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)


# ------------------------------------------------------------------
# Deep merge utility
# ------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge override into base.
    Override values win. Nested dicts are merged, not replaced.
    Returns a new dict — base and override are not mutated.
    """
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


# ------------------------------------------------------------------
# Built-in defaults — used when no config file is found,
# and as the base that config file values are merged onto.
# Every key here mirrors a key in claudebox.config.yaml.
# ------------------------------------------------------------------

_DEFAULTS: dict[str, Any] = {
    "api": {
        "api_key": None,
        "api_key_source": "env",
        "api_key_env_var": "CLAUDE_API_KEY",
        "auth_token": None,
        "base_url": None,
        "anthropic_version": "2023-06-01",
        "default_headers": {},
        "default_query": {},
        "strict_response_validation": False,
    },
    "keyring": {
        "service_name": "claudebox",
        "username": "claude_api_key",
    },
    "connection": {
        "timeout_total": 600.0,
        "timeout_connect": 10.0,
        "timeout_read": 300.0,
        "timeout_write": 30.0,
        "max_retries": 2,
        "proxy": None,
        "follow_redirects": True,
        "max_connections": 100,
        "max_keepalive_connections": 20,
        "keepalive_expiry": 5.0,
        "local_address": None,
    },
    "model": {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "temperature": None,
        "top_p": None,
        "top_k": None,
        "stop_sequences": [],
        "service_tier": None,
    },
    "system": {
        "prompt": None,
        "cache_control": False,
        "cache_control_type": "ephemeral",
    },
    "thinking": {
        "enabled": False,
        "budget_tokens": 5000,
        "stream_thinking": True,
    },
    "conversation": {
        "multi_session": True,
        "default_session_id": "default",
        "max_history_messages": None,
        "truncation_strategy": "drop_oldest",
        "auto_clear_after_turn": False,
        "prefill": None,
        "include_prefill_in_response": True,
    },
    "streaming": {
        "enabled": True,
        "use_stream_helpers": True,
        "yield_raw_events": False,
        "thread_mode": "direct",
    },
    "tools": {
        "tool_choice": "auto",
        "auto_run_tools": True,
        "max_tool_iterations": 10,
        "default_tool_timeout": 30.0,
        "validate_tool_inputs": True,
        "include_tool_blocks_in_response": True,
        "include_tool_results_in_history": True,
    },
    "vision": {
        "default_media_type": "image/jpeg",
        "max_image_size_bytes": 5242880,
        "auto_resize": False,
        "auto_resize_target_bytes": 4000000,
        "auto_encode_from_path": True,
    },
    "files": {
        "enabled": False,
        "beta_header": "files-api-2025-04-14",
        "default_upload_media_type": "application/octet-stream",
        "cache_uploads": False,
        "max_upload_size_bytes": None,
    },
    "batches": {
        "poll_interval_seconds": 60,
        "auto_poll": True,
        "max_poll_wait_seconds": None,
        "stream_results": True,
        "raise_on_partial_failure": False,
    },
    "events": {
        "enabled": True,
        "async_handlers": False,
        "handler_thread_pool_size": 4,
        "suppress_handler_errors": True,
        "allow_unknown_events": False,
    },
    "cache": {
        "enabled": False,
        "auto_cache_system_prompt": False,
        "auto_cache_history": False,
        "auto_cache_history_n": 2,
    },
    "beta": {
        "interleaved_thinking": False,
        "interleaved_thinking_header": "interleaved-thinking-2025-05-14",
        "code_execution": False,
        "code_execution_header": "code-execution-2025-05-22",
        "files_api": False,
        "files_api_header": "files-api-2025-04-14",
        "mcp_connector": False,
        "mcp_connector_header": "mcp-client-2025-04-04",
        "extended_output": False,
        "extended_output_header": "output-128k-2025-02-19",
        "computer_use": False,
        "computer_use_header": "computer-use-2025-01-24",
        "token_counting": False,
        "token_counting_header": "token-counting-2024-11-01",
        "prompt_caching": False,
        "prompt_caching_header": "prompt-caching-2024-07-31",
        "message_batches": False,
        "message_batches_header": "message-batches-2024-09-24",
        "fine_tuning": False,
        "fine_tuning_header": "fine-tuning-2024-11-15",
        "extra_beta_headers": [],
    },
    "metadata": {
        "user_id": None,
        "extra": {},
    },
    "logging": {
        "level": "warning",
        "sdk_log_level": "off",
        "logger_name": "claudebox",
        "log_requests": False,
        "log_responses": False,
        "log_token_usage": True,
        "log_tool_calls": True,
        "log_events": False,
        "log_to_file": False,
        "log_file_path": "claudebox.log",
        "log_file_max_bytes": 10485760,
        "log_file_backup_count": 3,
        "log_format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        "log_request_id": True,
    },
    "platform": {
        "provider": "anthropic",
        "bedrock": {
            "aws_region": None,
            "aws_access_key": None,
            "aws_secret_key": None,
            "aws_session_token": None,
            "aws_profile": None,
        },
        "vertex": {
            "project_id": None,
            "region": "us-east5",
            "credentials": None,
        },
    },
}
