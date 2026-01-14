from datetime import datetime
from pydantic import BaseModel


class StudySession(BaseModel):
    id: int | None = None
    task: str
    category: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: int = 0
    mode: str
    school_week: int
    paused_seconds: int = 0


class TimerState(BaseModel):
    session_id: int | None = None
    is_running: bool = False
    is_paused: bool = False
    mode: str = "stopwatch"
    started_at: datetime | None = None
    paused_at: datetime | None = None
    pomodoro_phase: str | None = None
    pomodoro_cycle: int = 0
    phase_started_at: datetime | None = None
