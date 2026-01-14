import json
from pathlib import Path
from pydantic import BaseModel

CONFIG_FILE = Path(__file__).parent / "data" / "config.json"

DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15
DEFAULT_SESSIONS_UNTIL_LONG = 4


class PomodoroConfig(BaseModel):
    work_minutes: int = DEFAULT_WORK_MINUTES
    short_break_minutes: int = DEFAULT_SHORT_BREAK_MINUTES
    long_break_minutes: int = DEFAULT_LONG_BREAK_MINUTES
    sessions_until_long_break: int = DEFAULT_SESSIONS_UNTIL_LONG


def load_config() -> PomodoroConfig:
    if not CONFIG_FILE.exists():
        return PomodoroConfig()

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    return PomodoroConfig(**data)


def save_config(config: PomodoroConfig) -> None:
    CONFIG_FILE.parent.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
