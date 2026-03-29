🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████ ██    ██ ██ ████████ ███████  ▍
🮈  ██      ██    ██ ██    ██    ██       ▍
🮈  ███████ ██    ██ ██    ██    █████    ▍
🮈       ██ ██    ██ ██    ██    ██       ▍
🮈  ███████  ██████  ██    ██    ███████  ▍
🮈                                        ▍
🮈                                        ▍
🮈             Python Script              ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃

import json
from pathlib import Path

def load_suite():
    config_path = Path("~/.arca/config.json").expanduser()
    manifest_path_rel = Path("suite.manifest.json")

    with open(config_path) as f:
        config = json.load(f)

    suite_root = Path(config["suite_root"])
    manifest_path = suite_root / manifest_path_rel

    with open(manifest_path) as f:
        manifest = json.load(f)

    return config, manifest, suite_root

def resolve(suite_root, relative_path):
    return suite_root / relative_path

