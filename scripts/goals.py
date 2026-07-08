from dataclasses import dataclass, field
from datetime import datetime, timedelta, time


@dataclass
class AmountGoal:
    target_amount: float
    current_amount: float = 0
    user_input: str # "input/options"
    input_divisions: float
    unit: str = ""

    def progress(self):
        return self.current_amount / self.target_amount

@dataclass
class ActionGoal:
    done: bool = False
    current_count: int = 0
    action_name: str = ""

    def progress(self):
        return self.current_count / self.target_count


@dataclass
class TimeGoal:
    target_duration: timedelta
    accumulated: timedelta = field(default_factory=timedelta)

    def progress(self) -> float:
        return min(self.accumulated / self.target_duration, 1.0) if self.target_duration else 0.0


@dataclass
class Goal:
    title: str
    description: str
    goal_type: str          # "amount" | "action" | "time"
    goal: object            # AmountGoal() / ActionGoal() / TimeGoal() instance

    def progress(self) -> float:
        return self.goal.progress()

    def is_complete(self) -> bool:
        return self.progress() >= 1.0


@dataclass
class DailyGoal:
    goal: Goal
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        self.assigned_time = datetime.combine(today, time.min)
        self.finish_time = datetime.combine(today, time.max)

    def left_time(self) -> float:
        pass
        # return left_hours / 24


@dataclass
class WeeklyGoal:
    goal: Goal
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        self.assigned_time = datetime.combine(start_of_week, time.min)
        self.finish_time = datetime.combine(end_of_week, time.max)

    def left_time(self) -> float:
        pass
        # return left_days / 7


@dataclass
class CustomGoal:
    goal: Goal
    assigned_time: datetime
    finish_time: datetime

    def left_time(self) -> float:
        pass
        # return left_hours / total_hours