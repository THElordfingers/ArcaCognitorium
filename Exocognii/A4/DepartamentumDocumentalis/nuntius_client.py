# Departamentum Documentalis · nuntius_client.py · v1.1
import requests
from DepartamentumDocumentalis.config import CFG

def emit(channel: str, payload: dict) -> None:
    try:
        requests.post(
            f"{CFG['nuntius_api']}/observe",
            json={"channel": channel, "source": "III-DD", "payload": payload},
            timeout=2)
    except Exception:
        pass
