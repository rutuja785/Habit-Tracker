"""
scheduler.py — lightweight APScheduler wrapper for habit reminders.

Because Streamlit re-runs the entire script on every interaction,
we store the scheduler in st.session_state so it is only started once
per browser session. Real push notifications require a native OS hook
(not available in a web app), so we simulate reminders by surfacing
a banner inside the UI when the reminder time is within ±5 minutes of now.
"""

from datetime import datetime, time as dtime
from apscheduler.schedulers.background import BackgroundScheduler
import streamlit as st


_SCHEDULER_KEY = "_habit_scheduler"


def get_scheduler() -> BackgroundScheduler:
    if _SCHEDULER_KEY not in st.session_state:
        scheduler = BackgroundScheduler()
        scheduler.start()
        st.session_state[_SCHEDULER_KEY] = scheduler
    return st.session_state[_SCHEDULER_KEY]


def due_reminders(habits: list[dict]) -> list[str]:
    """
    Return names of habits whose reminder_time is within ±5 min of now.
    Called every render to show an in-app banner.
    """
    now = datetime.now().time()
    due = []
    for h in habits:
        rt = h.get("reminder_time")
        if not rt:
            continue
        try:
            hh, mm = map(int, rt.split(":"))
            reminder = dtime(hh, mm)
            delta = abs(
                (now.hour * 60 + now.minute) - (reminder.hour * 60 + reminder.minute)
            )
            if delta <= 5:
                due.append(h["name"])
        except ValueError:
            pass
    return due