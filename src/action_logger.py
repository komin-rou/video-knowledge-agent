from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_PATH = LOG_DIR / "agent_actions.log"


class ActionLogger:
    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        print(log_line)