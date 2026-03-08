# Changelog

All notable changes to ClaudeBox will be documented here.

Format: [Semantic Versioning](https://semver.org) — `MAJOR.MINOR.PATCH`

---

## [0.1.0] — Initial Release

### Added
- `ClaudeBox` core engine with sync, async, threaded, and generator interfaces
- Full multi-session conversation management
- Streaming via events, generators, and callbacks
- Tool use with auto-registration, schema extraction, and auto-run loop
- Vision and image input (base64 and URL)
- Files API integration (beta)
- Message Batches API
- Extended thinking support
- Full event bus with 34 named events and auto-generated shorthand methods
- `claudebox.config.yaml` control panel — 18 sections, every option exposed
- Complete exception hierarchy — 40+ exception types
- Typed dataclass models for all inputs and outputs
- AWS Bedrock and Google Vertex AI platform support
- Hot-reload config at runtime
- Secure API key storage via system keyring
- Per-session config overrides
- Per-request config overrides
- Prompt caching support
- Beta feature flag management
- Full logging configuration with file rotation
