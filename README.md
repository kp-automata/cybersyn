# Cybersyn

```
   ______      __
  / ____/_  __/ /_  ___  ____________  ________
 / /   / / / / __ \/ _ \/ ___/ ___/ / / / __ \
/ /___/ /_/ / /_/ /  __/ /  (__  ) /_/ / / / /
\____/\__, /_.___/\___/_/  /____/\__, /_/ /_/
     /____/                     /____/
```

Study tracker and timer with analytics.

## Setup

```bash
uv sync
```

Add alias to your shell config (~/.bashrc or ~/.zshrc):

```bash
alias cybersyn="uv run --directory /path/to/cybersyn main.py"
```

Replace `/path/to/cybersyn` with your local repo path.

Reload shell or source the config.

## Usage

### Stopwatch Mode

```bash
cybersyn start "Assignment 1" --category "Analysis 1" --week 1
```

Timer runs in foreground with live display. Press Ctrl+C to detach (timer keeps running).

```bash
cybersyn status
cybersyn pause
cybersyn resume
cybersyn stop
```

### Pomodoro Mode

```bash
cybersyn start "Preread chapter 15.1" --category "Multivariable Calclus 2" --week 1 --pomodoro
```

Auto-cycles through work/break periods with notifications.

Default: 25min work, 5min short break, 15min long break (every 4 sessions).

```bash
cybersyn config
cybersyn config --work 30 --short-break 10
cybersyn config --long-break 20 --sessions 3
```

### View Sessions

```bash
cybersyn list
cybersyn list --limit 20
```

### Statistics

```bash
cybersyn stats
cybersyn stats --days 7
```

Shows session count, total time, breakdown by category.

### Charts

```bash
cybersyn charts
cybersyn show
```

Generates time series, category breakdown, and heat map calendar.

### Export

```bash
cybersyn export
cybersyn export backup.csv
```

## Features

- Stopwatch and Pomodoro modes
- Pause/resume functionality
- System notifications (notify-send)
- Session persistence (survives crashes)
- Live timer display
- SQLite storage
- Analytics and visualizations
- CSV export

## Data

- Database: `data/cybersyn.db`
- State: `data/state.json`
- Config: `data/config.json`
- Charts: `data/charts/`

## Help

```bash
cybersyn --help
cybersyn start --help
```
