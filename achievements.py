from dataclasses import dataclass


@dataclass
class Badge:
    id: str
    emoji: str
    name: str
    description: str
    unlocked: bool = False


BADGE_DEFINITIONS = [
    Badge("first_habit",    "🌱", "First Habit",       "Created your very first habit"),
    Badge("streak_3",       "🎯", "Hat Trick",          "3-day streak on any habit"),
    Badge("streak_7",       "🔥", "Week Warrior",       "7-day streak on any habit"),
    Badge("streak_14",      "💪", "Fortnight Fighter",  "14-day streak on any habit"),
    Badge("streak_30",      "⚡", "Monthly Master",     "30-day streak on any habit"),
    Badge("streak_100",     "👑", "100-Day Legend",     "100-day streak on any habit"),
    Badge("goal_reached",   "🏆", "Goal Crusher",       "Reached your streak target"),
    Badge("multi_habit",    "🎪", "Habit Collector",    "Tracking 3 or more habits"),
    Badge("perfect_week",   "✨", "Perfect Week",       "All habits completed for 7 days"),
]

_BADGE_MAP = {b.id: b for b in BADGE_DEFINITIONS}


def evaluate_badges(habits: list[dict]) -> list[Badge]:
    """
    Given a list of habit dicts (from DB), return a list of Badge objects
    with unlocked=True/False based on current state.
    """
    results = [Badge(b.id, b.emoji, b.name, b.description, False) for b in BADGE_DEFINITIONS]
    badge_map = {b.id: b for b in results}

    if habits:
        badge_map["first_habit"].unlocked = True

    if len(habits) >= 3:
        badge_map["multi_habit"].unlocked = True

    max_current = max((h["current_streak"] for h in habits), default=0)
    max_longest = max((h["longest_streak"] for h in habits), default=0)
    best = max(max_current, max_longest)

    if best >= 3:
        badge_map["streak_3"].unlocked = True
    if best >= 7:
        badge_map["streak_7"].unlocked = True
    if best >= 14:
        badge_map["streak_14"].unlocked = True
    if best >= 30:
        badge_map["streak_30"].unlocked = True
    if best >= 100:
        badge_map["streak_100"].unlocked = True

    if any(h["current_streak"] >= h["target_streak"] for h in habits):
        badge_map["goal_reached"].unlocked = True

    return results


def unlocked_count(badges: list[Badge]) -> int:
    return sum(1 for b in badges if b.unlocked)