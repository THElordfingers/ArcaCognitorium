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


def test_subscriber_receives_published_payload(running_bus):
    received = []
    sub = MundanaClient()
    sub.connect()
    sub.subscribe("mundana.horologica", lambda p: received.append(p))

    pub = MundanaClient()
    pub.connect()
    pub.publish("mundana.horologica", {"unix_ts": 1712600000})
    time.sleep(0.2)

    assert received, "No payload received"
    assert received[0]["unix_ts"] == 1712600000
    sub.disconnect()
    pub.disconnect()


def test_multiple_subscribers_all_receive(running_bus):
    buckets = [[], [], []]
    clients = []
    for i in range(3):
        c = MundanaClient()
        c.connect()
        idx = i
        c.subscribe("mundana.app_status", lambda p, i=idx: buckets[i].append(p))
        clients.append(c)

    pub = MundanaClient()
    pub.connect()
    pub.publish("mundana.app_status", {"app": "praesidium", "alive": True})
    time.sleep(0.2)

    for i, bucket in enumerate(buckets):
        assert bucket, f"Subscriber {i} received nothing"
        assert bucket[0]["app"] == "praesidium"

    for c in clients:
        c.disconnect()
    pub.disconnect()


def test_publish_to_different_channel_not_received(running_bus):
    received = []
    sub = MundanaClient()
    sub.connect()
    sub.subscribe("mundana.horologica", lambda p: received.append(p))

    pub = MundanaClient()
    pub.connect()
    pub.publish("mundana.tidalis", {"phase": "neap"})
    time.sleep(0.15)

    assert not received, "Should not receive message on different channel"
    sub.disconnect()
    pub.disconnect()
