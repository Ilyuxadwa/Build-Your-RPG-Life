from dataclasses import dataclass, field
from datetime import datetime, timedelta, time

@dataclass
class AmountGoal:
    target_amount: float
    current_amount: float = 0.0
    unit: str = ""

    def progress(self) -> float:
        return min(self.current_amount / self.target_amount, 1.0) if self.target_amount else 0.0


@dataclass
class ActionGoal:
    target_count: int
    current_count: int = 0
    action_name: str = ""

    def progress(self) -> float:
        return min(self.current_count / self.target_count, 1.0) if self.target_count else 0.0


@dataclass
class TimeGoal:
    target_duration: timedelta
    accumulated: timedelta = field(default_factory=timedelta)

    def progress(self) -> float:
        return min(self.accumulated / self.target_duration, 1.0) if self.target_duration else 0.0



@dataclass(kw_only=True)
class Goal:
    assigned_time: datetime
    finish_time: datetime
    title: str
    goal_type: str
    goal: object

    def progress(self) -> float:
        return self.goal.progress()

    def is_complete(self) -> bool:
        return self.progress() >= 1.0



@dataclass(kw_only=True)
class DailyGoal(Goal):
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        self.assigned_time = datetime.combine(today, time.min)
        self.finish_time = datetime.combine(today, time.max)


@dataclass(kw_only=True)
class WeeklyGoal(Goal):
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()


@dataclass(kw_only=True)
class CustomGoal(Goal):
    pass

