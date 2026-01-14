import subprocess
import shutil


def send_notification(title: str, message: str, urgency: str = "normal") -> bool:
    if not shutil.which("notify-send"):
        return False

    try:
        subprocess.run(
            ["notify-send", "-u", urgency, title, message],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def notify_session_started(task: str, mode: str) -> None:
    send_notification(
        "Cybersyn - Session Started",
        f"{mode.capitalize()}: {task}",
        urgency="normal",
    )


def notify_session_paused(elapsed: str) -> None:
    send_notification(
        "Cybersyn - Timer Paused",
        f"Elapsed: {elapsed}",
        urgency="low",
    )


def notify_session_resumed() -> None:
    send_notification(
        "Cybersyn - Timer Resumed",
        "Back to work!",
        urgency="low",
    )


def notify_session_stopped(task: str, duration: str) -> None:
    send_notification(
        "Cybersyn - Session Complete",
        f"{task}\nTotal time: {duration}",
        urgency="normal",
    )


def notify_pomodoro_work_end() -> None:
    send_notification(
        "Cybersyn - Time for a Break!",
        "Work session complete. Take a break.",
        urgency="critical",
    )


def notify_pomodoro_break_end() -> None:
    send_notification(
        "Cybersyn - Break Over",
        "Time to get back to work!",
        urgency="critical",
    )
