import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta


# ── Colour palette (matches app theme) ───────────────────────────────────────
EMPTY_COLOR   = "#1e2130"
FILL_COLORS   = ["#0d3b1e", "#1a6b38", "#27a35a", "#34d679", "#4fffab"]
ACCENT        = "#34d679"
BG            = "#0e1117"
SURFACE       = "#1a1d2e"
TEXT          = "#e8eaf0"


# ── GitHub-style Calendar Heatmap ─────────────────────────────────────────────

def calendar_heatmap(logs: list[dict], habit_name: str, weeks: int = 18) -> go.Figure:
    """
    Render a GitHub-contribution-style weekly grid.
    rows = Mon–Sun (0–6), cols = week buckets.
    """
    today = date.today()
    start = today - timedelta(weeks=weeks - 1)
    # Align to Monday
    start -= timedelta(days=start.weekday())

    completed_set = {
        log["date"] for log in logs if log["completed"]
    }

    all_days: list[date] = []
    d = start
    while d <= today:
        all_days.append(d)
        d += timedelta(days=1)

    # Build grid: shape (7, num_weeks)
    num_weeks = (len(all_days) + 6) // 7
    z       = [[None] * num_weeks for _ in range(7)]
    text    = [[""] * num_weeks for _ in range(7)]
    week_labels = [""] * num_weeks

    for i, day in enumerate(all_days):
        col = i // 7
        row = day.weekday()          # 0=Mon … 6=Sun
        val = 1 if str(day) in completed_set else 0
        if day > today:
            z[row][col]    = None
        else:
            z[row][col]    = val
        text[row][col] = f"{day.strftime('%b %d %Y')}<br>{'✓ Done' if val else '✗ Missed'}"
        if row == 0:
            week_labels[col] = day.strftime("%b %d")

    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=list(range(num_weeks)),
            y=day_labels,
            text=text,
            hovertemplate="%{text}<extra></extra>",
            colorscale=[
                [0.0, EMPTY_COLOR],
                [0.5, EMPTY_COLOR],
                [0.5, ACCENT],
                [1.0, FILL_COLORS[4]],
            ],
            showscale=False,
            xgap=3,
            ygap=3,
            zmin=0,
            zmax=1,
        )
    )

    fig.update_layout(
        title=dict(text=f"Activity — {habit_name}", font=dict(color=TEXT, size=15)),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT),
        margin=dict(l=50, r=10, t=40, b=30),
        height=220,
        xaxis=dict(
            tickvals=list(range(0, num_weeks, 2)),
            ticktext=[week_labels[i] for i in range(0, num_weeks, 2)],
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(showgrid=False, zeroline=False, autorange="reversed"),
    )
    return fig


# ── Progress Ring ─────────────────────────────────────────────────────────────

def progress_ring(current: int, target: int, habit_name: str) -> go.Figure:
    pct = min(100, round(current / max(target, 1) * 100))
    remaining = 100 - pct

    fig = go.Figure(
        go.Pie(
            values=[pct, remaining],
            hole=0.72,
            marker_colors=[ACCENT, EMPTY_COLOR],
            textinfo="none",
            hoverinfo="skip",
            direction="clockwise",
            sort=False,
        )
    )

    fig.add_annotation(
        text=f"<b>{pct}%</b>",
        x=0.5, y=0.55,
        font=dict(size=28, color=ACCENT),
        showarrow=False,
    )
    fig.add_annotation(
        text=f"{current} / {target}",
        x=0.5, y=0.35,
        font=dict(size=13, color=TEXT),
        showarrow=False,
    )
    fig.add_annotation(
        text=habit_name[:18],
        x=0.5, y=0.18,
        font=dict(size=11, color="#8892b0"),
        showarrow=False,
    )

    fig.update_layout(
        showlegend=False,
        paper_bgcolor=BG,
        margin=dict(l=10, r=10, t=10, b=10),
        height=180,
    )
    return fig


# ── Weekly Bar Chart ──────────────────────────────────────────────────────────

def weekly_bar(logs: list[dict]) -> go.Figure:
    """Last 7-day completion bars across all habits (or single habit)."""
    today = date.today()
    days  = [today - timedelta(days=i) for i in range(6, -1, -1)]
    completed_dates = {log["date"] for log in logs if log["completed"]}

    vals   = [1 if str(d) in completed_dates else 0 for d in days]
    labels = [d.strftime("%d %b") for d in days]
    colors = [ACCENT if v else EMPTY_COLOR for v in vals]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=vals,
            marker_color=colors,
            text=["✓" if v else "" for v in vals],
            textposition="inside",
            textfont=dict(color=BG, size=14),
            hovertemplate="%{x}<extra></extra>",
        )
    )
    # fig.update_layout(
    #     paper_bgcolor=BG,
    #     plot_bgcolor=BG,
    #     font=dict(color=TEXT),
    #     margin=dict(l=10, r=10, t=10, b=10),
    #     height=150,
    #     yaxis=dict(visible=False, range=[0, 1.4]),
    #     xaxis=dict(showgrid=False, zeroline=False),
    #     bargap=0.3,
    # )
    # return fig

    fig.update_layout(
        xaxis=dict(type="category"),
        yaxis=dict(visible=False, range=[0, 1.4]),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT),
    )

    return fig

    


# ── Multi-habit Completion Rate (last 30 days) ────────────────────────────────

def multi_habit_bar(habits_with_pct: list[dict]) -> go.Figure:
    """
    habits_with_pct: [{"name": str, "pct": float}, …]
    """
    if not habits_with_pct:
        return go.Figure()

    names = [h["name"][:20] for h in habits_with_pct]
    pcts  = [h["pct"] for h in habits_with_pct]
    colors = [ACCENT if p >= 70 else "#f59e0b" if p >= 40 else "#ef4444" for p in pcts]

    fig = go.Figure(
        go.Bar(
            x=pcts,
            y=names,
            orientation="h",
            marker_color=colors,
            text=[f"{p:.0f}%" for p in pcts],
            textposition="auto",
            textfont=dict(color=BG, size=13),
        )
    )
    fig.update_layout(
        title=dict(text="30-Day Completion Rate", font=dict(color=TEXT, size=14)),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT),
        margin=dict(l=10, r=10, t=40, b=10),
        height=max(140, 50 * len(habits_with_pct)),
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )
    return fig