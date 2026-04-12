# Departamentum Documentalis · workers.py · v1.1
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.signals.finished.emit(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.signals.error.emit(str(e))
