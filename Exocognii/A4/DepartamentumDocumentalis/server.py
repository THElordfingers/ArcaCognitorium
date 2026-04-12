# Departamentum Documentalis · server.py · v1.2
import threading
import socket
import uvicorn

PORT = 8733

def is_port_bound(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def start() -> bool:
    if is_port_bound(PORT):
        return False

    def _run():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from DepartamentumDocumentalis.api import app
        cfg = uvicorn.Config(app, host="127.0.0.1", port=PORT,
                             log_level="warning", loop="asyncio")
        srv = uvicorn.Server(cfg)
        loop.run_until_complete(srv.serve())

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return True
