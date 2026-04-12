# tests/test_client_degraded.py
# Mundana State Bus v1.0
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pathlib import Path
from mundana_client import MundanaClient, BusDaemonNotRunningError

# Ensure no daemon is running for these tests
SOCKET_PATH = Path("/tmp/mundana.sock")


@pytest.fixture(autouse=True)
def no_socket():
    SOCKET_PATH.unlink(missing_ok=True)
    yield
    SOCKET_PATH.unlink(missing_ok=True)


def test_connect_raises_when_daemon_absent():
    client = MundanaClient()
    with pytest.raises(BusDaemonNotRunningError):
        client.connect()


def test_degraded_mode_pattern():
    """Canonical degraded mode: catch, set flag, continue."""
    bus_active = True
    client = MundanaClient()
    try:
        client.connect()
    except BusDaemonNotRunningError:
        bus_active = False

    assert not bus_active


def test_publish_is_noop_when_not_connected():
    """publish() must not raise if socket is None."""
    client = MundanaClient()
    # Do not connect — should be silent no-op
    client.publish("mundana.horologica", {"unix_ts": 0})


def test_disconnect_is_safe_when_not_connected():
    client = MundanaClient()
    client.disconnect()  # must not raise
