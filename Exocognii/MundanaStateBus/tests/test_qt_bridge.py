# tests/test_qt_bridge.py
# Mundana State Bus v1.0
#
# Requires PyQt6 in the active Python environment.
# Run with: pytest tests/test_qt_bridge.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading
import time
import pytest

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QObject, pyqtSignal
    HAS_QT = True
except ImportError:
    HAS_QT = False

pytestmark = pytest.mark.skipif(not HAS_QT, reason="PyQt6 not available")

from mundana_bus import MundanaBus, SOCKET_PATH
from mundana_client import MundanaClient
from mundana_qt_bridge import MundanaQtBridge


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv[:1])
    yield app


@pytest.fixture
def running_bus():
    bus = MundanaBus()
    t = threading.Thread(target=bus.start, daemon=True)
    t.start()
    for _ in range(20):
        if SOCKET_PATH.exists():
            break
        time.sleep(0.05)
    yield bus
    bus._running = False
    if bus._server_sock:
        try:
            bus._server_sock.close()
        except OSError:
            pass
    SOCKET_PATH.unlink(missing_ok=True)
    time.sleep(0.1)


def test_qt_bridge_dispatches_on_main_thread(qapp, running_bus):
    main_thread_id = threading.main_thread().ident
    dispatch_thread_ids = []

    class Receiver(QObject):
        tick = pyqtSignal(dict)

        def __init__(self):
            super().__init__()
            self.tick.connect(
                lambda p: dispatch_thread_ids.append(threading.current_thread().ident)
            )

    recv = Receiver()
    bridge = MundanaQtBridge("mundana.horologica", recv.tick)
    bridge.connect()

    pub = MundanaClient()
    pub.connect()
    pub.publish("mundana.horologica", {"unix_ts": 42})
    time.sleep(0.15)
    qapp.processEvents()
    time.sleep(0.05)
    qapp.processEvents()

    assert dispatch_thread_ids, "Bridge callback never fired"
    assert dispatch_thread_ids[0] == main_thread_id, (
        f"Callback fired on thread {dispatch_thread_ids[0]}, "
        f"expected main thread {main_thread_id}"
    )

    bridge.disconnect()
    pub.disconnect()


def test_qt_bridge_degraded_when_no_daemon(qapp):
    from mundana_client import BusDaemonNotRunningError
    from pathlib import Path
    Path("/tmp/mundana.sock").unlink(missing_ok=True)

    class Receiver(QObject):
        tick = pyqtSignal(dict)

    recv = Receiver()
    bridge = MundanaQtBridge("mundana.horologica", recv.tick)

    with pytest.raises(BusDaemonNotRunningError):
        bridge.connect()
