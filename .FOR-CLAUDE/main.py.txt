#╔══════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/main.py
#║ ⛨
#╚══════════════════════════════════════════════════════════


import os
from client.config import AppConfig
from ui.app import ChatTUIApp


def main() -> None:
    cfg = AppConfig.load("config.yaml")

    api_key = cfg.api.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key. Set OPENAI_API_KEY or api.api_key in config.yaml")

    ChatTUIApp(cfg, api_key=api_key).run()


if __name__ == "__main__":
    main()
