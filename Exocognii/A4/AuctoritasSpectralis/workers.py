# Auctoritas Spectralis — workers.py
# v1.0.0
"""QRunnable workers for non-blocking IO operations."""

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal


class WorkerSignals(QObject):
    """Signals emitted by background workers."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)


class IoWorker(QRunnable):
    """Execute a callable on the thread pool."""

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        """Execute the callable; emit result or error."""
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
