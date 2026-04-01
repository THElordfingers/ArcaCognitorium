#╔══════════════════════════════════════════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/__main__.py
#║ ⛨
#╚══════════════════════════════════════════════════════════


import os
from client.config import AppConfig
from ui.app import ChatTUIApp


def main() -> None:
    cfg = AppConfig.load("config.yaml")

    env_var = cfg.api.get("api_key_env_var", "CLAUDE_API_KEY")
    api_key = cfg.api.api_key or os.environ.get(env_var)
    if not api_key:
        raise RuntimeError(f"Missing API key. Set {env_var} or api.api_key in config.yaml")

    ChatTUIApp(cfg, api_key=api_key).run()


if __name__ == "__main__":
    main()
