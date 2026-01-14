import json
from pathlib import Path
from models import TimerState

STATE_FILE = Path(__file__).parent / "data" / "state.json"


def load_state() -> TimerState:
    if not STATE_FILE.exists():
        return TimerState()

    with open(STATE_FILE, "r") as f:
        data = json.load(f)

    return TimerState(**data)


def save_state(state: TimerState) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)

    with open(STATE_FILE, "w") as f:
        json.dump(state.model_dump(mode="json"), f, indent=2, default=str)


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
