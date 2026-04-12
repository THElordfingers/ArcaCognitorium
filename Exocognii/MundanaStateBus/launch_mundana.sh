#!/usr/bin/env bash
BUS_DIR="${HOME}/ArcaCognitorium/Exocognii/MundanaStateBus"
PARENT_DIR="${HOME}/ArcaCognitorium/Exocognii"
PID_FILE="/tmp/mundana.pid"
SOCK_FILE="/tmp/mundana.sock"
LOG_DIR="${HOME}/.local/share/exocognii"
LOG_FILE="${LOG_DIR}/mundana.log"

if command -v pyenv &>/dev/null; then
    PYTHON="$(pyenv which python3 2>/dev/null || echo "")"
fi
if [[ -z "${PYTHON}" ]] || [[ ! -x "${PYTHON}" ]]; then
    PYTHON="$(command -v python3)"
fi

mkdir -p "${LOG_DIR}"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo "[mundana] Already running (PID $(cat "${PID_FILE}"))"
    exit 0
fi

echo "[mundana] Starting — Python: ${PYTHON}  PYTHONPATH: ${PARENT_DIR}"
export PYTHONPATH="${PARENT_DIR}"
cd "${PARENT_DIR}"

"${PYTHON}" -m MundanaStateBus >> "${LOG_FILE}" 2>&1 &

ATTEMPTS=0
while [[ ! -S "${SOCK_FILE}" ]] && [[ ${ATTEMPTS} -lt 10 ]]; do
    sleep 0.2
    (( ATTEMPTS++ ))
done

if [[ -S "${SOCK_FILE}" ]]; then
    echo "[mundana] Live — socket at ${SOCK_FILE}"
    # Start Machinae Bridge
    "${PYTHON}" -m MundanaStateBus.mundana_machinae_bridge >> "${LOG_DIR}/mundana_bridge.log" 2>&1 &
    echo "[mundana] Machinae bridge started (PID $!)"
else
    echo "[mundana] ERROR: Bus failed to start — see ${LOG_FILE}" >&2
    exit 1
fi
