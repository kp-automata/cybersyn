from datetime import datetime
from models import TimerState
from config import load_config


def get_phase_duration(phase: str) -> int:
    cfg = load_config()
    if phase == "work":
        return cfg.work_minutes * 60
    elif phase == "short_break":
        return cfg.short_break_minutes * 60
    elif phase == "long_break":
        return cfg.long_break_minutes * 60
    return 0


def get_phase_remaining(state: TimerState) -> int:
    if not state.phase_started_at or not state.pomodoro_phase:
        return 0

    elapsed = (datetime.now() - state.phase_started_at).total_seconds()
    duration = get_phase_duration(state.pomodoro_phase)
    remaining = int(duration - elapsed)

    return max(0, remaining)


def should_transition(state: TimerState) -> bool:
    return get_phase_remaining(state) <= 0


def get_next_phase(state: TimerState) -> tuple[str, int]:
    cfg = load_config()

    if state.pomodoro_phase == "work":
        new_cycle = state.pomodoro_cycle + 1
        if new_cycle >= cfg.sessions_until_long_break:
            return "long_break", 0
        else:
            return "short_break", new_cycle

    return "work", state.pomodoro_cycle


def transition_phase(state: TimerState) -> tuple[TimerState, str]:
    next_phase, next_cycle = get_next_phase(state)

    state.pomodoro_phase = next_phase
    state.pomodoro_cycle = next_cycle
    state.phase_started_at = datetime.now()

    return state, next_phase


def init_pomodoro_state(state: TimerState) -> TimerState:
    state.pomodoro_phase = "work"
    state.pomodoro_cycle = 0
    state.phase_started_at = datetime.now()
    return state
