import typer
import time
import subprocess
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from timer import (
    start_session,
    pause_session,
    resume_session,
    stop_session,
    get_current_status,
)
from database import get_session, get_all_sessions, delete_session, save_session
from models import StudySession
from notify import (
    notify_session_started,
    notify_session_paused,
    notify_session_resumed,
    notify_session_stopped,
    notify_pomodoro_work_end,
    notify_pomodoro_break_end,
)
from pomodoro import get_phase_remaining, should_transition, transition_phase
from state import save_state
from stats import get_total_time, get_time_by_category, get_sessions_last_n_days, get_session_count
from analytics import generate_all_charts
from config import load_config, save_config

app = typer.Typer(help="Cybersyn - Study tracker and timer")


def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


@app.command()
def start(
    task: str,
    category: str = typer.Option(..., "--category", "-c", help="Study category/class"),
    week: int = typer.Option(..., "--week", "-w", help="School week number"),
    pomodoro: bool = typer.Option(False, "--pomodoro", "-p", help="Use pomodoro mode"),
):
    """Start a new study session"""
    try:
        mode = "pomodoro" if pomodoro else "stopwatch"
        session = start_session(task, category, week, mode)
        notify_session_started(task, mode)
        typer.echo(f"Started {mode} session: {task}")
        typer.echo(f"Category: {category} | Week: {week}")
        typer.echo("\nTimer running... (Ctrl+C to detach)")

        try:
            while True:
                result = get_current_status()
                if not result:
                    break
                state, elapsed = result

                if mode == "pomodoro":
                    if should_transition(state):
                        state, next_phase = transition_phase(state)
                        save_state(state)

                        if next_phase == "work":
                            notify_pomodoro_break_end()
                            typer.echo(f"\n\nBreak over! Starting work session {state.pomodoro_cycle + 1}")
                        elif next_phase == "short_break":
                            notify_pomodoro_work_end()
                            typer.echo("\n\nWork session complete! Time for a short break.")
                        elif next_phase == "long_break":
                            notify_pomodoro_work_end()
                            typer.echo("\n\nWork session complete! Time for a long break.")

                    remaining = get_phase_remaining(state)
                    phase_display = state.pomodoro_phase.replace("_", " ").title()
                    typer.echo(f"\r⏱  {phase_display}: {format_duration(remaining)} | Total: {format_duration(elapsed)}", nl=False)
                else:
                    typer.echo(f"\r⏱  {format_duration(elapsed)}", nl=False)

                time.sleep(1)
        except KeyboardInterrupt:
            typer.echo("\n\nTimer detached. Session still running in background.")
            typer.echo("Use 'cybersyn status' to check, 'cybersyn pause' to pause, or 'cybersyn stop' to end.")

    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def pause():
    """Pause the current timer"""
    try:
        session_id, elapsed = pause_session()
        duration_str = format_duration(elapsed)
        notify_session_paused(duration_str)
        typer.echo(f"Timer paused at {duration_str}")
        typer.echo("Use 'cybersyn resume' to continue, or 'cybersyn stop' to end session.")
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def resume():
    """Resume the paused timer"""
    try:
        session_id, elapsed = resume_session()
        notify_session_resumed()
        typer.echo(f"Timer resumed from {format_duration(elapsed)}")
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def stop():
    """Stop the current session"""
    try:
        session = stop_session()
        duration_str = format_duration(session.duration_seconds)
        notify_session_stopped(session.task, duration_str)
        typer.echo(f"Session stopped: {session.task}")
        typer.echo(f"Total time: {duration_str}")
        if session.paused_seconds > 0:
            typer.echo(f"Paused time: {format_duration(session.paused_seconds)}")
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def status():
    """Show current timer status"""
    result = get_current_status()
    if not result:
        typer.echo("No active session")
        return

    state, elapsed = result
    session = get_session(state.session_id)

    if not session:
        typer.echo("Error: Session not found")
        return

    typer.echo(f"Task: {session.task}")
    typer.echo(f"Category: {session.category} | Week: {session.school_week}")
    typer.echo(f"Mode: {session.mode}")

    if session.mode == "pomodoro" and state.pomodoro_phase:
        remaining = get_phase_remaining(state)
        phase_display = state.pomodoro_phase.replace("_", " ").title()
        typer.echo(f"Phase: {phase_display} ({format_duration(remaining)} remaining)")
        typer.echo(f"Cycle: {state.pomodoro_cycle + 1}")

    typer.echo(f"Elapsed: {format_duration(elapsed)}")
    if state.is_paused:
        typer.echo("Status: PAUSED")
    else:
        typer.echo("Status: RUNNING")


@app.command()
def list(limit: int = typer.Option(10, "--limit", "-n", help="Number of sessions to show")):
    """List recent study sessions"""
    sessions = get_all_sessions()

    if not sessions:
        typer.echo("No sessions found")
        return

    sessions = sessions[:limit]

    typer.echo(f"\nShowing last {len(sessions)} sessions:\n")
    typer.echo(f"{'ID':<5} {'Date':<12} {'Task':<30} {'Category':<15} {'Duration':<10} {'Mode':<10}")
    typer.echo("-" * 90)

    for s in sessions:
        date_str = s.start_time.strftime("%Y-%m-%d")
        task_str = s.task[:28] + ".." if len(s.task) > 30 else s.task
        category_str = s.category[:13] + ".." if len(s.category) > 15 else s.category
        duration_str = format_duration(s.duration_seconds)
        typer.echo(f"{s.id:<5} {date_str:<12} {task_str:<30} {category_str:<15} {duration_str:<10} {s.mode:<10}")


@app.command()
def delete(
    session_id: int = typer.Argument(..., help="Session ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete a session permanently"""
    session = get_session(session_id)

    if not session:
        typer.echo(f"Error: Session {session_id} not found", err=True)
        raise typer.Exit(1)

    # Show session details
    typer.echo(f"\nSession to delete:")
    typer.echo(f"  ID: {session.id}")
    typer.echo(f"  Task: {session.task}")
    typer.echo(f"  Category: {session.category}")
    typer.echo(f"  Date: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    typer.echo(f"  Duration: {format_duration(session.duration_seconds)}")
    typer.echo(f"  Mode: {session.mode}")

    # Confirmation prompt
    if not force:
        confirm = typer.confirm("\nAre you sure you want to delete this session permanently?")
        if not confirm:
            typer.echo("Deletion cancelled")
            return

    # Delete the session
    if delete_session(session_id):
        typer.echo(f"\nSession {session_id} deleted successfully")
    else:
        typer.echo(f"Error: Failed to delete session {session_id}", err=True)
        raise typer.Exit(1)


@app.command()
def stats(
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Limit to last N days"),
):
    """Show study statistics"""
    sessions = get_all_sessions()

    if not sessions:
        typer.echo("No sessions found")
        return

    if days:
        sessions = get_sessions_last_n_days(sessions, days)

    total = get_total_time(sessions)
    count = get_session_count(sessions)
    by_category = get_time_by_category(sessions)

    typer.echo(f"\nSessions: {count}")
    typer.echo(f"Total: {format_duration(total)}")
    typer.echo(f"\nBy category:")
    for cat, time in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        typer.echo(f"  {cat}: {format_duration(time)}")


@app.command()
def charts(
    dashboard: bool = typer.Option(False, "--dashboard", "-d", help="Generate dashboard view only")
):
    """Generate visualization charts"""
    sessions = get_all_sessions()

    if not sessions:
        typer.echo("No sessions found")
        return

    if dashboard:
        typer.echo("Generating dashboard...")
    else:
        typer.echo("Generating charts...")

    chart_files = generate_all_charts(sessions, dashboard_only=dashboard)

    if chart_files:
        typer.echo(f"\nGenerated {len(chart_files)} chart{'s' if len(chart_files) > 1 else ''}:")
        for chart in chart_files:
            typer.echo(f"  {chart}")
    else:
        typer.echo("No charts generated")


@app.command()
def show():
    """Open chart viewer"""
    charts_dir = Path(__file__).parent / "data" / "charts"

    if not charts_dir.exists() or not any(charts_dir.glob("*.png")):
        typer.echo("No charts found. Run 'cybersyn charts' first.")
        return

    chart_files = sorted(charts_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not chart_files:
        typer.echo("No charts found. Run 'cybersyn charts' first.")
        return

    typer.echo(f"Opening {len(chart_files[:3])} most recent charts...")
    for chart in chart_files[:3]:
        subprocess.run(["xdg-open", str(chart)])


@app.command()
def export(output: str = typer.Argument("sessions.csv")):
    """Export sessions to CSV"""
    import csv

    sessions = get_all_sessions()

    if not sessions:
        typer.echo("No sessions to export")
        return

    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'task', 'category', 'start_time', 'end_time', 'duration_seconds', 'mode', 'school_week', 'paused_seconds'])

        for s in sessions:
            writer.writerow([
                s.id,
                s.task,
                s.category,
                s.start_time.isoformat(),
                s.end_time.isoformat() if s.end_time else '',
                s.duration_seconds,
                s.mode,
                s.school_week,
                s.paused_seconds
            ])

    typer.echo(f"Exported {len(sessions)} sessions to {output}")


@app.command()
def add(
    task: str,
    category: str = typer.Option(..., "--category", "-c", help="Study category/class"),
    week: int = typer.Option(..., "--week", "-w", help="School week number"),
    duration: int = typer.Option(..., "--duration", "-d", help="Duration in minutes"),
    date: Optional[str] = typer.Option(None, "--date", help="Date in YYYY-MM-DD format (defaults to today)"),
    mode: str = typer.Option("manual", "--mode", "-m", help="Mode type"),
):
    """Manually add a completed study session"""
    if duration <= 0:
        typer.echo("Error: Duration must be greater than 0", err=True)
        raise typer.Exit(1)

    if date:
        try:
            session_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            typer.echo("Error: Date must be in YYYY-MM-DD format", err=True)
            raise typer.Exit(1)

        if session_date.date() > datetime.now().date():
            typer.echo("Error: Date cannot be in the future", err=True)
            raise typer.Exit(1)
    else:
        session_date = datetime.now()

    start_time = session_date.replace(hour=12, minute=0, second=0, microsecond=0)
    duration_seconds = duration * 60
    end_time = start_time + timedelta(seconds=duration_seconds)

    session = StudySession(
        task=task,
        category=category,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        mode=mode,
        school_week=week,
    )

    session_id = save_session(session)

    typer.echo(f"Added session #{session_id}")
    typer.echo(f"Task: {task}")
    typer.echo(f"Category: {category} | Week: {week}")
    typer.echo(f"Date: {start_time.strftime('%Y-%m-%d')}")
    typer.echo(f"Duration: {format_duration(duration_seconds)}")
    typer.echo(f"Mode: {mode}")


@app.command()
def config(
    work: Optional[int] = typer.Option(None, "--work", "-w", help="Work duration in minutes"),
    short_break: Optional[int] = typer.Option(None, "--short-break", "-s", help="Short break in minutes"),
    long_break: Optional[int] = typer.Option(None, "--long-break", "-l", help="Long break in minutes"),
    sessions: Optional[int] = typer.Option(None, "--sessions", "-n", help="Work sessions until long break"),
    show: bool = typer.Option(False, "--show", help="Show current config"),
):
    """Configure pomodoro settings"""
    cfg = load_config()

    if show or (work is None and short_break is None and long_break is None and sessions is None):
        typer.echo("Current pomodoro configuration:")
        typer.echo(f"  Work duration: {cfg.work_minutes} minutes")
        typer.echo(f"  Short break: {cfg.short_break_minutes} minutes")
        typer.echo(f"  Long break: {cfg.long_break_minutes} minutes")
        typer.echo(f"  Sessions until long break: {cfg.sessions_until_long_break}")
        return

    if work is not None:
        cfg.work_minutes = work
    if short_break is not None:
        cfg.short_break_minutes = short_break
    if long_break is not None:
        cfg.long_break_minutes = long_break
    if sessions is not None:
        cfg.sessions_until_long_break = sessions

    save_config(cfg)
    typer.echo("Pomodoro configuration updated:")
    typer.echo(f"  Work duration: {cfg.work_minutes} minutes")
    typer.echo(f"  Short break: {cfg.short_break_minutes} minutes")
    typer.echo(f"  Long break: {cfg.long_break_minutes} minutes")
    typer.echo(f"  Sessions until long break: {cfg.sessions_until_long_break}")


if __name__ == "__main__":
    app()
