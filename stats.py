from datetime import datetime, timedelta
from collections import defaultdict
from models import StudySession


def get_total_time(sessions: list[StudySession]) -> int:
    return sum(s.duration_seconds for s in sessions)


def get_time_by_category(sessions: list[StudySession]) -> dict[str, int]:
    by_category = defaultdict(int)
    for s in sessions:
        by_category[s.category] += s.duration_seconds
    return dict(by_category)


def get_time_by_week(sessions: list[StudySession]) -> dict[int, int]:
    by_week = defaultdict(int)
    for s in sessions:
        by_week[s.school_week] += s.duration_seconds
    return dict(by_week)


def get_time_by_mode(sessions: list[StudySession]) -> dict[str, int]:
    by_mode = defaultdict(int)
    for s in sessions:
        by_mode[s.mode] += s.duration_seconds
    return dict(by_mode)


def get_sessions_last_n_days(sessions: list[StudySession], days: int) -> list[StudySession]:
    cutoff = datetime.now() - timedelta(days=days)
    return [s for s in sessions if s.start_time >= cutoff]


def get_average_session_duration(sessions: list[StudySession]) -> int:
    if not sessions:
        return 0
    return get_total_time(sessions) // len(sessions)


def get_longest_session(sessions: list[StudySession]) -> StudySession | None:
    if not sessions:
        return None
    return max(sessions, key=lambda s: s.duration_seconds)


def get_session_count(sessions: list[StudySession]) -> int:
    return len(sessions)


def get_time_by_date(sessions: list[StudySession]) -> dict[str, int]:
    by_date = defaultdict(int)
    for s in sessions:
        date_str = s.start_time.strftime("%Y-%m-%d")
        by_date[date_str] += s.duration_seconds
    return dict(by_date)
