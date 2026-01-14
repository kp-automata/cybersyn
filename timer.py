import time
from datetime import datetime
from models import StudySession, TimerState
from state import load_state, save_state, clear_state
from database import save_session, update_session
from pomodoro import init_pomodoro_state


def start_session(task: str, category: str, week: int, mode: str = "stopwatch") -> StudySession:
    state = load_state()
    if state.is_running:
        raise RuntimeError("A session is already running. Stop it first.")

    session = StudySession(
        task=task,
        category=category,
        start_time=datetime.now(),
        mode=mode,
        school_week=week,
    )

    session_id = save_session(session)
    session.id = session_id

    new_state = TimerState(
        session_id=session_id,
        is_running=True,
        mode=mode,
        started_at=datetime.now(),
    )

    if mode == "pomodoro":
        new_state = init_pomodoro_state(new_state)

    save_state(new_state)

    return session


def pause_session() -> tuple[int, int]:
    state = load_state()
    if not state.is_running:
        raise RuntimeError("No active session to pause.")
    if state.is_paused:
        raise RuntimeError("Session is already paused.")

    state.is_paused = True
    state.paused_at = datetime.now()
    save_state(state)

    elapsed = get_elapsed_seconds(state)
    return state.session_id, elapsed


def resume_session() -> tuple[int, int]:
    state = load_state()
    if not state.is_running:
        raise RuntimeError("No active session to resume.")
    if not state.is_paused:
        raise RuntimeError("Session is not paused.")

    if state.paused_at and state.started_at:
        pause_duration = (datetime.now() - state.paused_at).total_seconds()
        state.started_at = datetime.fromtimestamp(
            state.started_at.timestamp() + pause_duration
        )

    state.is_paused = False
    state.paused_at = None
    save_state(state)

    elapsed = get_elapsed_seconds(state)
    return state.session_id, int(elapsed)


def stop_session() -> StudySession:
    state = load_state()
    if not state.is_running:
        raise RuntimeError("No active session to stop.")

    elapsed = get_elapsed_seconds(state)
    paused_seconds = 0

    if state.paused_at and state.started_at:
        paused_seconds = int((datetime.now() - state.paused_at).total_seconds())

    update_session(
        state.session_id,
        end_time=datetime.now(),
        duration_seconds=int(elapsed),
        paused_seconds=paused_seconds,
    )

    clear_state()

    from database import get_session
    return get_session(state.session_id)


def get_current_status() -> tuple[TimerState, int] | None:
    state = load_state()
    if not state.is_running:
        return None

    elapsed = get_elapsed_seconds(state)
    return state, int(elapsed)


def get_elapsed_seconds(state: TimerState) -> float:
    if not state.started_at:
        return 0.0

    if state.is_paused and state.paused_at:
        return (state.paused_at - state.started_at).total_seconds()

    return (datetime.now() - state.started_at).total_seconds()
