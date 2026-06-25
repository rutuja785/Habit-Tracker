from datetime import date, timedelta
from database import get_logs_for_habit, update_streaks


def recalc_streaks(habit_id: int) -> tuple[int, int]:
    """
    Recalculate current and longest streaks for a habit.
    Current streak: consecutive completed days ending today (or yesterday if today not logged yet).
    Longest streak: the longest run of consecutive completed days ever.
    Returns (current_streak, longest_streak).
    """
    logs = get_logs_for_habit(habit_id)          # ordered DESC by date
    if not logs:
        update_streaks(habit_id, 0, 0)
        return 0, 0

    # Build a set of completed dates
    completed_dates = {
        date.fromisoformat(log["date"])
        for log in logs
        if log["completed"]
    }

    if not completed_dates:
        update_streaks(habit_id, 0, 0)
        return 0, 0

    today = date.today()

    # ── Current streak ────────────────────────────────────────────────────────
    # Walk backwards from today
    current = 0
    cursor = today
    while cursor in completed_dates:
        current += 1
        cursor -= timedelta(days=1)

    # If today not completed yet, try from yesterday
    if current == 0:
        cursor = today - timedelta(days=1)
        while cursor in completed_dates:
            current += 1
            cursor -= timedelta(days=1)

    # ── Longest streak ────────────────────────────────────────────────────────
    sorted_dates = sorted(completed_dates)
    longest = 1
    run = 1
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    update_streaks(habit_id, current, longest)
    return current, longest


def get_streak_label(current: int) -> str:
    """Return a motivational label based on the current streak length."""
    if current == 0:
        return "Start your streak today! 🌱"
    if current == 1:
        return "Day 1 — great start! 🎯"
    if current < 7:
        return f"{current} days — keep going! 🔥"
    if current < 14:
        return f"{current} days — one week done! 💪"
    if current < 30:
        return f"{current} days — two weeks strong! 🚀"
    if current < 100:
        return f"{current} days — you're on fire! ⚡"
    return f"{current} days — LEGENDARY! 👑"


def streak_completion_message(habit_name: str, target: int) -> str:
    return (
        f"🎉 **Congratulations!** You've completed the "
        f"**{target}-Day {habit_name} Challenge!**\n\n"
        f"Ready for the next level? Choose your next goal below."
    )