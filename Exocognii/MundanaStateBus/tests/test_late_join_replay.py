import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading
import time
import pytest
from mundana_bus import MundanaBus, SOCKET_PATH
from mundana_client import MundanaClient, BusDaemonNotRunningError


@pytest.fixture
def running_bus():
    """Start MundanaBus in a daemon thread; wait for socket; yield; stop cleanly."""
    bus = MundanaBus()
    ready = threading.Event()

    def _run():
        # Patch accept to set ready after bind
        orig_listen = bus._server_sock.__class__.listen if False else None
        bus.start.__func__  # just to touch it
        # Start normally — socket appears once bind+listen complete
        bus.start()

    # We need to know when the socket file exists.
    # Start in thread, poll for socket file.
    t = threading.Thread(target=bus.start, daemon=True)
    t.start()

    deadline = time.monotonic() + 3.0
    while not SOCKET_PATH.exists():
        if time.monotonic() > deadline:
            pytest.fail("Mundana State Bus socket did not appear within 3s")
        time.sleep(0.02)

    yield bus

    bus.stop()
    t.join(timeout=2.0)
    SOCKET_PATH.unlink(missing_ok=True)


def test_late_subscriber_receives_last_state(running_bus):
    pub = MundanaClient()
    pub.connect()
    pub.publish("mundana.horologica", {"unix_ts": 9999, "iso": "2026-04-08T00:00:00"})
    time.sleep(0.1)
    pub.disconnect()

    received = []
    sub = MundanaClient()
    sub.connect()
    sub.subscribe("mundana.horologica", lambda p: received.append(p))
    time.sleep(0.2)

    assert received, "Late subscriber received no REPLAY"
    assert received[0]["unix_ts"] == 9999
    sub.disconnect()


def test_no_replay_on_unpublished_channel(running_bus):
    received = []
    sub = MundanaClient()
    sub.connect()
    sub.subscribe("mundana.solaris", lambda p: received.append(p))
    time.sleep(0.2)

    assert not received, "Should not receive REPLAY on channel with no prior publish"
    sub.disconnect()


def test_replay_is_most_recent_payload(running_bus):
    pub = MundanaClient()
    pub.connect()
    for ts in [1, 2, 3]:
        pub.publish("mundana.horologica", {"unix_ts": ts})
        time.sleep(0.03)
    pub.disconnect()
    time.sleep(0.1)

    received = []
    sub = MundanaClient()
    sub.connect()
    sub.subscribe("mundana.horologica", lambda p: received.append(p))
    time.sleep(0.2)

    assert received, "No REPLAY received"
    assert received[0]["unix_ts"] == 3, "REPLAY should carry most recent payload"
    sub.disconnect()
