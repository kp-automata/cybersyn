from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import numpy as np
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
    ax.plot(dates, hours, marker='o', linewidth=2, markersize=6, label='Daily Hours', color='#2E86AB')

    if len(dates) >= 3:
        x_numeric = np.arange(len(dates))
        z = np.polyfit(x_numeric, hours, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(x_numeric), "--", linewidth=2, label='Trend', color='#C73E1D', alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    ax.set_title('Study Sessions Over Time')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
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
    total_hours = sum(hours)

    sorted_data = sorted(zip(categories, hours), key=lambda x: x[1], reverse=True)
    categories, hours = zip(*sorted_data)

    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#C73E1D', '#6A4C93', '#E63946', '#06FFA5']
    bar_colors = [colors[i % len(colors)] for i in range(len(categories))]

    min_date = min(s.start_time.date() for s in sessions)
    max_date = max(s.start_time.date() for s in sessions)
    date_range = f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}"

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, hours, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.2)

    for bar in bars:
        height = bar.get_height()
        percentage = (height / total_hours) * 100
        ax.text(bar.get_x() + bar.get_width() / 2., height,
               f'({percentage:.0f}%)',
               ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Category')
    ax.set_ylabel('Hours')
    ax.set_title(f'Study Time by Category: {date_range}')
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


def generate_time_of_day(sessions: list[StudySession]) -> Path:
    by_hour = defaultdict(int)
    for s in sessions:
        hour = s.start_time.hour
        by_hour[hour] += s.duration_seconds / 3600

    if not by_hour:
        return None

    hours = list(range(24))
    values = [by_hour.get(h, 0) for h in hours]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(hours, values, color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1)

    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Total Hours Studied')
    ax.set_title('Study Time by Hour of Day')
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    output = CHARTS_DIR / f"time_of_day_{get_timestamp()}.png"
    plt.savefig(output, dpi=150)
    plt.close()
    return output


def generate_dashboard(sessions: list[StudySession]) -> Path:
    if not sessions:
        return None

    fig = plt.figure(figsize=(20, 11))
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.3)

    ax_time_series = fig.add_subplot(gs[0, :])
    ax_category = fig.add_subplot(gs[1, 0])
    ax_heatmap = fig.add_subplot(gs[1, 1])
    ax_time_of_day = fig.add_subplot(gs[1, 2])

    by_date = defaultdict(int)
    for s in sessions:
        date = s.start_time.date()
        by_date[date] += s.duration_seconds / 3600

    if by_date:
        dates = sorted(by_date.keys())
        hours = [by_date[d] for d in dates]

        ax_time_series.plot(dates, hours, marker='o', linewidth=2, markersize=6, label='Daily Hours', color='#2E86AB')

        if len(dates) >= 3:
            x_numeric = np.arange(len(dates))
            z = np.polyfit(x_numeric, hours, 1)
            p = np.poly1d(z)
            ax_time_series.plot(dates, p(x_numeric), "--", linewidth=2, label='Trend', color='#C73E1D', alpha=0.7)

        ax_time_series.set_xlabel('Date')
        ax_time_series.set_ylabel('Hours')
        ax_time_series.set_title('Study Sessions Over Time')
        ax_time_series.grid(True, alpha=0.3)
        ax_time_series.legend(loc='best')
        ax_time_series.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax_time_series.tick_params(axis='x', rotation=45)

    by_category = defaultdict(int)
    for s in sessions:
        by_category[s.category] += s.duration_seconds / 3600

    if by_category:
        categories = list(by_category.keys())
        cat_hours = list(by_category.values())
        total_hours = sum(cat_hours)

        sorted_data = sorted(zip(categories, cat_hours), key=lambda x: x[1], reverse=True)
        categories, cat_hours = zip(*sorted_data)

        colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#C73E1D', '#6A4C93', '#E63946', '#06FFA5']
        bar_colors = [colors[i % len(colors)] for i in range(len(categories))]

        min_date = min(s.start_time.date() for s in sessions)
        max_date = max(s.start_time.date() for s in sessions)
        date_range = f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}"

        bars = ax_category.bar(categories, cat_hours, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.2)

        for bar in bars:
            height = bar.get_height()
            percentage = (height / total_hours) * 100
            ax_category.text(bar.get_x() + bar.get_width() / 2., height,
                           f'({percentage:.0f}%)',
                           ha='center', va='bottom', fontsize=8)

        ax_category.set_xlabel('Category')
        ax_category.set_ylabel('Hours')
        ax_category.set_title(f'Study Time by Category: {date_range}')
        ax_category.grid(True, alpha=0.3, axis='y')
        ax_category.tick_params(axis='x', rotation=45)

    by_date_heat = defaultdict(float)
    for s in sessions:
        date = s.start_time.date()
        by_date_heat[date] += s.duration_seconds / 3600

    if by_date_heat:
        min_date = min(by_date_heat.keys())
        max_date = max(by_date_heat.keys())

        start_date = min_date - timedelta(days=min_date.weekday())
        end_date = max_date + timedelta(days=(6 - max_date.weekday()))

        weeks = []
        current = start_date
        while current <= end_date:
            week = []
            for _ in range(7):
                week.append(by_date_heat.get(current, 0))
                current += timedelta(days=1)
            weeks.append(week)

        data = list(zip(*weeks))

        im = ax_heatmap.imshow(data, aspect='auto', cmap='YlGn', interpolation='nearest')

        ax_heatmap.set_yticks(range(7))
        ax_heatmap.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        ax_heatmap.set_xticks([])
        ax_heatmap.set_title('Study Activity Heatmap')
        ax_heatmap.grid(False)

        plt.colorbar(im, ax=ax_heatmap, label='Hours', fraction=0.046, pad=0.04)

    by_hour = defaultdict(int)
    for s in sessions:
        hour = s.start_time.hour
        by_hour[hour] += s.duration_seconds / 3600

    if by_hour:
        hours_day = list(range(24))
        values = [by_hour.get(h, 0) for h in hours_day]

        ax_time_of_day.bar(hours_day, values, color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1)

        ax_time_of_day.set_xlabel('Hour of Day')
        ax_time_of_day.set_ylabel('Total Hours')
        ax_time_of_day.set_title('Study Time by Hour of Day')
        ax_time_of_day.set_xticks(range(0, 24, 4))
        ax_time_of_day.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 4)])
        ax_time_of_day.grid(True, alpha=0.3, axis='y')

    output = CHARTS_DIR / f"dashboard_{get_timestamp()}.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    return output


def generate_all_charts(sessions: list[StudySession], dashboard_only: bool = False) -> list[Path]:
    charts = []

    if dashboard_only:
        chart = generate_dashboard(sessions)
        if chart:
            charts.append(chart)
    else:
        chart = generate_time_series(sessions)
        if chart:
            charts.append(chart)

        chart = generate_category_breakdown(sessions)
        if chart:
            charts.append(chart)

        chart = generate_heatmap(sessions)
        if chart:
            charts.append(chart)

        chart = generate_time_of_day(sessions)
        if chart:
            charts.append(chart)

    return charts
