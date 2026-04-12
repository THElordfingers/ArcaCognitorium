
#!/usr/bin/env bash
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨  ARCANUM BRIDGE LAUNCHER  ⯩      𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
##  launch_bridge.sh
###
####  Starts the Arcanum Bridge FastAPI server
#####   Exports env vars, activates pyenv, fires uvicorn
######

set -euo pipefail

# ── Paths ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_SCRIPT="${SCRIPT_DIR}/mcp_bridge_server.py"
ENV_FILE="${SCRIPT_DIR}/.env"
PYENV_PYTHON="${HOME}/.pyenv/versions/3.11.9/bin/python"
FALLBACK_PYTHON="python3"

# ── Load .env if present ─────────────────────────────────────────
if [[ -f "${ENV_FILE}" ]]; then
    echo "  ⯨ loading .env"
    set -o allexport
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +o allexport
fi

# ── Validate required env vars ───────────────────────────────────
if [[ -z "${BRIDGE_API_KEY:-}" ]]; then
    echo "  ⚠  BRIDGE_API_KEY is not set."
    echo "     Add it to ${ENV_FILE} or export it before running."
    exit 1
fi

if [[ -z "${CLAUDE_API_KEY:-}" ]]; then
    echo "  ⚠  CLAUDE_API_KEY is not set."
    echo "     Add it to ${ENV_FILE} or export it before running."
    exit 1
fi

# ── Choose Python ────────────────────────────────────────────────
if [[ -x "${PYENV_PYTHON}" ]]; then
    PYTHON="${PYENV_PYTHON}"
else
    PYTHON="${FALLBACK_PYTHON}"
fi

echo ""
echo "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"
echo "⯨  ARCANUM BRIDGE  ⯩         𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ"
echo "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"
echo "  Python  : ${PYTHON}"
echo "  Script  : ${BRIDGE_SCRIPT}"
echo "  Port    : ${BRIDGE_PORT:-7432}"
echo "  Vault   : ${HOME}/ArcaCognitorium"
# Print Tailscale IP if available
if command -v tailscale &>/dev/null; then
    TAILSCALE_IP="$(tailscale ip -4 2>/dev/null || echo 'not connected')"
    echo "  Tailscale: ${TAILSCALE_IP}:${BRIDGE_PORT:-7432}"
fi
echo "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"
echo ""

# ── Install deps if needed ───────────────────────────────────────
"${PYTHON}" -c "import fastapi, anthropic, uvicorn" 2>/dev/null || {
    echo "  ⯨ installing dependencies…"
    "${PYTHON}" -m pip install fastapi anthropic uvicorn httpx --quiet
}

# ── Launch ───────────────────────────────────────────────────────
exec "${PYTHON}" "${BRIDGE_SCRIPT}"
