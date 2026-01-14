from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from models import StudySession

CHARTS_DIR = Path(__file__).parent / "data" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_time_series(sessions: list[StudySession]) -> Path:
    by_date = defaultdict(int)
    for s in sessions:
        date = s.start_time.date()
        by_date[date] += s.duration_seconds / 3600

    if not by_date:
        return None

    dates = sorted(by_date.keys())
    hours = [by_date[d] for d in dates]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, hours, marker='o', linewidth=2, markersize=6)
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    ax.set_title('Study Time Over Time')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output = CHARTS_DIR / f"time_series_{get_timestamp()}.png"
    plt.savefig(output, dpi=150)
    plt.close()
    return output


def generate_category_breakdown(sessions: list[StudySession]) -> Path:
    by_category = defaultdict(int)
    for s in sessions:
        by_category[s.category] += s.duration_seconds / 3600

    if not by_category:
        return None

    categories = list(by_category.keys())
    hours = list(by_category.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, hours)
    ax.set_xlabel('Category')
    ax.set_ylabel('Hours')
    ax.set_title('Study Time by Category')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output = CHARTS_DIR / f"category_breakdown_{get_timestamp()}.png"
    plt.savefig(output, dpi=150)
    plt.close()
    return output


def generate_heatmap(sessions: list[StudySession]) -> Path:
    by_date = defaultdict(float)
    for s in sessions:
        date = s.start_time.date()
        by_date[date] += s.duration_seconds / 3600

    if not by_date:
        return None

    min_date = min(by_date.keys())
    max_date = max(by_date.keys())

    start_date = min_date - timedelta(days=min_date.weekday())
    end_date = max_date + timedelta(days=(6 - max_date.weekday()))

    weeks = []
    current = start_date
    while current <= end_date:
        week = []
        for _ in range(7):
            week.append(by_date.get(current, 0))
            current += timedelta(days=1)
        weeks.append(week)

    data = list(zip(*weeks))

    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(data, aspect='auto', cmap='YlGn', interpolation='nearest')

    ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    ax.set_xticks([])
    ax.set_title('Study Activity Heatmap')

    plt.colorbar(im, ax=ax, label='Hours')
    plt.tight_layout()

    output = CHARTS_DIR / f"heatmap_{get_timestamp()}.png"
    plt.savefig(output, dpi=150)
    plt.close()
    return output


def generate_all_charts(sessions: list[StudySession]) -> list[Path]:
    charts = []

    chart = generate_time_series(sessions)
    if chart:
        charts.append(chart)

    chart = generate_category_breakdown(sessions)
    if chart:
        charts.append(chart)

    chart = generate_heatmap(sessions)
    if chart:
        charts.append(chart)

    return charts
