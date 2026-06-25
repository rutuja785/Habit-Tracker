"""
app.py — Habit Tracker main entry point.
Run with:  streamlit run app.py
"""

import streamlit as st
from datetime import date, timedelta
import sys, os
from datetime import time
from html import escape

# Ensure local modules resolve regardless of CWD
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from streak import recalc_streaks, get_streak_label, streak_completion_message
from achievements import evaluate_badges, unlocked_count
from charts import calendar_heatmap, progress_ring, weekly_bar, multi_habit_bar
from styles import inject_css
from scheduler import due_reminders

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HabitFlow",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
db.init_db()

TODAY = str(date.today())

# ── Motivational quotes ───────────────────────────────────────────────────────
QUOTES = [
    "\"We are what we repeatedly do. Excellence, then, is not an act, but a habit.\" — Aristotle",
    "\"Motivation is what gets you started. Habit is what keeps you going.\" — Jim Ryun",
    "\"You'll never change your life until you change something you do daily.\" — John C. Maxwell",
    "\"Small daily improvements are the key to staggering long-term results.\"",
    "\"Success is the sum of small efforts repeated day in and day out.\" — Robert Collier",
    "\"The secret of your future is hidden in your daily routine.\" — Mike Murdock",
]

import hashlib
_quote_idx = int(hashlib.md5(TODAY.encode()).hexdigest(), 16) % len(QUOTES)
DAILY_QUOTE = QUOTES[_quote_idx]


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — navigation + add habit
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🔥 HabitFlow")
    st.markdown(f"*{date.today().strftime('%A, %B %d %Y')}*")
    st.divider()

    page = st.radio(
        "Navigate",
        ["📋 Today", "📅 Calendar & History", "📊 Dashboard", "🏆 Achievements", "⚙️ Manage Habits"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### ➕ New Habit")

    with st.form("add_habit_form", clear_on_submit=True):
        new_name = st.text_input("Habit name", placeholder="e.g. Morning Run")
        new_desc = st.text_area("Description (optional)", height=70)
        new_target = st.selectbox(
            "Streak goal",
            [7, 14, 21, 30, 60, 100],
            format_func=lambda x: f"{x} Days",
        )
        custom_target = st.number_input("Or enter custom days", min_value=1, max_value=365, value=7, step=1)
        use_custom = st.checkbox("Use custom goal")
        new_reminder = st.time_input("Daily reminder (optional)", value=time(8, 0))
        submitted = st.form_submit_button("Create Habit", use_container_width=True)

        if submitted and new_name.strip():
            target = int(custom_target) if use_custom else int(new_target)
            reminder_str = new_reminder.strftime("%H:%M") if new_reminder else None
            db.create_habit(new_name.strip(), new_desc.strip(), reminder_str, target)
            st.success(f"✅ '{new_name.strip()}' created!")
            st.rerun()

    st.divider()
    st.caption(f"💬 *{DAILY_QUOTE}*")


# ── Fetch all habits ──────────────────────────────────────────────────────────
habits = db.get_all_habits()

# ── Reminder banners ──────────────────────────────────────────────────────────
reminders_due = due_reminders(habits)
for r in reminders_due:
    st.toast(f"⏰ Reminder: time to work on **{r}**!", icon="🔔")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TODAY
# ══════════════════════════════════════════════════════════════════════════════

if page == "📋 Today":
    st.markdown("## 📋 Today's Habits")
    st.markdown(f"Track your habits for **{date.today().strftime('%B %d, %Y')}**")

    if not habits:
        st.info("No habits yet. Add your first habit in the sidebar →")
    else:
        # Recalc all streaks on page load
        for h in habits:
            recalc_streaks(h["id"])
        habits = db.get_all_habits()   # refresh after recalc

        completed_today = 0

        for habit in habits:
            log = db.get_log_for_date(habit["id"], TODAY)
            is_done = log["completed"] if log else False

            col1, col2, col3 = st.columns([0.05, 0.65, 0.30])

            with col1:
                checked = st.checkbox("", value=is_done, key=f"chk_{habit['id']}")
                if checked != is_done:
                    db.log_habit(habit["id"], TODAY, checked)
                    recalc_streaks(habit["id"])
                    # Check if goal just reached
                    refreshed = db.get_habit(habit["id"])
                    if checked and refreshed and refreshed["current_streak"] >= refreshed["target_streak"]:
                        st.balloons()
                        st.success(streak_completion_message(habit["name"], habit["target_streak"]))
                    st.rerun()

            with col2:
                h_data = db.get_habit(habit["id"]) or habit
                streak_txt = get_streak_label(h_data["current_streak"])

                st.markdown(f"### {'✅' if is_done else '⬜'} {habit['name']}")

                if habit["description"]:
                    st.caption(habit["description"])

                st.success(streak_txt)

                if habit.get("reminder_time"):
                    st.caption(f"⏰ {habit['reminder_time']}")

            with col3:
                fig = progress_ring(h_data["current_streak"], h_data["target_streak"], habit["name"])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            if is_done:
                completed_today += 1

        # Daily summary
        st.divider()
        total = len(habits)
        pct   = int(completed_today / total * 100) if total else 0

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="metric-tile"><div class="metric-num">{completed_today}/{total}</div><div class="metric-label">Done Today</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-tile"><div class="metric-num">{pct}%</div><div class="metric-label">Completion Rate</div></div>""", unsafe_allow_html=True)
        best_streak = max((h["current_streak"] for h in habits), default=0)
        c3.markdown(f"""<div class="metric-tile"><div class="metric-num">🔥 {best_streak}</div><div class="metric-label">Best Active Streak</div></div>""", unsafe_allow_html=True)

        if pct == 100:
            st.success("🎉 **Perfect day!** All habits completed. You're on fire!")
        elif pct >= 50:
            st.info(f"💪 Halfway there — {total - completed_today} habit(s) left for today.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CALENDAR & HISTORY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📅 Calendar & History":
    st.markdown("## 📅 Calendar & History")

    if not habits:
        st.info("No habits yet. Add one in the sidebar.")
    else:
        selected_name = st.selectbox(
            "Select habit",
            [h["name"] for h in habits],
            key="cal_select",
        )
        habit = next(h for h in habits if h["name"] == selected_name)
        logs  = db.get_logs_for_habit(habit["id"])

        st.plotly_chart(
            calendar_heatmap(logs, habit["name"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown("#### Last 7 Days")
        st.plotly_chart(
            weekly_bar(logs),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        # Manual log editor
        st.divider()
        st.markdown("#### ✏️ Log a Past Date")
        with st.form("manual_log"):
            log_date = st.date_input("Date", value=date.today(), max_value=date.today())
            log_done = st.checkbox("Completed on this date")
            if st.form_submit_button("Save Log"):
                db.log_habit(habit["id"], str(log_date), log_done)
                recalc_streaks(habit["id"])
                st.success(f"Log saved for {log_date}.")
                st.rerun()

        # Raw log table
        with st.expander("📋 View full log"):
            if logs:
                import pandas as pd
                df = pd.DataFrame(logs)[["date", "completed"]]
                df["completed"] = df["completed"].map({1: "✅", 0: "❌", True: "✅", False: "❌"})
                df.columns = ["Date", "Status"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.write("No logs yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")

    if not habits:
        st.info("No habits yet.")
    else:
        # Recalc all
        for h in habits:
            recalc_streaks(h["id"])
        habits = db.get_all_habits()

        # Top-level stats
        c1, c2, c3, c4 = st.columns(4)
        total_habits  = len(habits)
        active_streaks = sum(1 for h in habits if h["current_streak"] > 0)
        best_current  = max((h["current_streak"] for h in habits), default=0)
        best_ever     = max((h["longest_streak"] for h in habits), default=0)

        c1.markdown(f'<div class="metric-tile"><div class="metric-num">{total_habits}</div><div class="metric-label">Total Habits</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-tile"><div class="metric-num">{active_streaks}</div><div class="metric-label">Active Streaks</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-tile"><div class="metric-num">🔥 {best_current}</div><div class="metric-label">Best Current</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-tile"><div class="metric-num">🏆 {best_ever}</div><div class="metric-label">All-Time Best</div></div>', unsafe_allow_html=True)

        st.divider()

        # 30-day completion rate per habit
        st.markdown("#### 30-Day Completion Rates")
        start_30 = str(date.today() - timedelta(days=29))
        rates = []
        for h in habits:
            logs = db.get_logs_date_range(h["id"], start_30, TODAY)
            done = sum(1 for l in logs if l["completed"])
            rates.append({"name": h["name"], "pct": round(done / 30 * 100, 1)})

        st.plotly_chart(
            multi_habit_bar(rates),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.divider()

        # Progress rings row
        st.markdown("#### Streak Progress")
        cols = st.columns(min(len(habits), 4))
        for i, h in enumerate(habits[:4]):
            with cols[i]:
                fig = progress_ring(h["current_streak"], h["target_streak"], h["name"])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown(
                    f"<div style='text-align:center;font-size:.82rem;color:#8892b0'>"
                    f"🔥 {h['current_streak']} day streak</div>",
                    unsafe_allow_html=True,
                )

        # Goal reached → suggest next challenge
        st.divider()
        for h in habits:
            if h["current_streak"] >= h["target_streak"]:
                st.success(streak_completion_message(h["name"], h["target_streak"]))
                st.markdown("**Choose your next challenge:**")
                nc1, nc2, nc3, nc4 = st.columns(4)
                next_goals = [14, 21, 30, 60]
                for col, goal in zip([nc1, nc2, nc3, nc4], next_goals):
                    if col.button(f"{goal} Days", key=f"next_{h['id']}_{goal}"):
                        db.update_habit(h["id"], h["name"], h["description"], h.get("reminder_time"), goal)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🏆 Achievements":
    st.markdown("## 🏆 Achievements")

    badges = evaluate_badges(habits)
    earned = unlocked_count(badges)
    total  = len(badges)

    st.markdown(f"**{earned} / {total} badges unlocked**")
    st.progress(earned / total if total else 0)

    st.divider()

    cols = st.columns(3)

    for i, badge in enumerate(badges):
        with cols[i % 3]:

            if badge.unlocked:
                st.success(f"{badge.emoji} {badge.name}")
            else:
                st.info(f"{badge.emoji} {badge.name} 🔒")

            st.caption(badge.description)

    if earned == total:
        st.balloons()
        st.success("🏆 **You've unlocked EVERY badge!** You are a true HabitFlow legend.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MANAGE HABITS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "⚙️ Manage Habits":
    st.markdown("## ⚙️ Manage Habits")

    if not habits:
        st.info("No habits to manage yet.")
    else:
        for habit in habits:
            with st.expander(f"✏️ {habit['name']}  —  🔥 {habit['current_streak']} day streak"):
                with st.form(f"edit_{habit['id']}"):
                    e_name = st.text_input("Name", value=habit["name"])
                    e_desc = st.text_area("Description", value=habit.get("description", ""), height=80)
                    e_target = st.number_input(
                        "Streak goal (days)",
                        min_value=1, max_value=365,
                        value=habit["target_streak"],
                    )
                    e_reminder = st.text_input(
                        "Reminder time (HH:MM, leave blank to remove)",
                        value=habit.get("reminder_time") or "",
                        placeholder="08:30",
                    )
                    col_save, col_del = st.columns([3, 1])
                    save = col_save.form_submit_button("💾 Save Changes", use_container_width=True)
                    delete = col_del.form_submit_button("🗑️ Delete", use_container_width=True)

                    if save:
                        reminder = e_reminder.strip() if e_reminder.strip() else None
                        db.update_habit(habit["id"], e_name.strip(), e_desc.strip(), reminder, int(e_target))
                        st.success("Saved!")
                        st.rerun()

                    if delete:
                        db.delete_habit(habit["id"])
                        st.warning(f"'{habit['name']}' deleted.")
                        st.rerun()

                # Stats summary
                st.markdown(
                    f"""
                    | Stat | Value |
                    |------|-------|
                    | Current Streak | 🔥 {habit['current_streak']} days |
                    | Longest Streak | 🏆 {habit['longest_streak']} days |
                    | Target | 🎯 {habit['target_streak']} days |
                    | Created | {habit['created_at']} |
                    """
                )