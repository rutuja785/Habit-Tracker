from dataclasses import dataclass, field
from datetime import date


@dataclass
class Habit:
    id: int
    name: str
    description: str = ""
    reminder_time: str | None = None
    target_streak: int = 7
    current_streak: int = 0
    longest_streak: int = 0
    created_at: str = field(default_factory=lambda: str(date.today()))

    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            reminder_time=d.get("reminder_time"),
            target_streak=d.get("target_streak", 7),
            current_streak=d.get("current_streak", 0),
            longest_streak=d.get("longest_streak", 0),
            created_at=d.get("created_at", str(date.today())),
        )

    @property
    def progress_pct(self) -> float:
        if self.target_streak == 0:
            return 0.0
        return min(100.0, round(self.current_streak / self.target_streak * 100, 1))

    @property
    def goal_reached(self) -> bool:
        return self.current_streak >= self.target_streak


@dataclass
class HabitLog:
    id: int
    habit_id: int
    date: str
    completed: bool

    @classmethod
    def from_dict(cls, d: dict) -> "HabitLog":
        return cls(
            id=d["id"],
            habit_id=d["habit_id"],
            date=d["date"],
            completed=bool(d["completed"]),
        )