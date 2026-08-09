from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Optional


class GoalStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class InputMode(Enum):
    PRESET = "preset"
    FREE = "free"
    TIMER = "timer"


@dataclass
class Goal:
    title: str
    description: str
    status: GoalStatus = GoalStatus.IN_PROGRESS
    stats: dict = field(default_factory=dict)
    additional_options: dict = field(default_factory=dict)
    recommended_for: list = field(default_factory=list)
    available_periods: dict = field(default_factory=dict)

    def progress(self) -> float:
        raise NotImplementedError

    def is_complete(self) -> bool:
        return self.progress() >= 1.0

    def cancel(self):
        self.status = GoalStatus.CANCELED

    def refresh_status(self):
        if self.status != GoalStatus.CANCELED:
            self.status = GoalStatus.COMPLETED if self.is_complete() else GoalStatus.IN_PROGRESS


@dataclass
class AmountGoal(Goal):
    target_amount: int = 0
    current_amount: int = 0
    unit: str = ""
    input_mode: InputMode = InputMode.FREE
    preset_options: list[int] = field(default_factory=list)

    def progress(self) -> float:
        return min(self.current_amount / self.target_amount, 1.0) if self.target_amount else 0.0

    def log(self, value: int):
        if self.input_mode == InputMode.PRESET and value not in self.preset_options:
            raise ValueError(f"{value} is not one of the preset options {self.preset_options}")
        self.current_amount += value
        self.refresh_status()


@dataclass
class ActionGoal(Goal):
    done: bool = False

    def progress(self) -> float:
        return 1.0 if self.done else 0.0

    def mark_done(self):
        self.done = True
        self.refresh_status()


@dataclass
class TimeGoal(Goal):
    target_duration: timedelta = field(default_factory=timedelta)
    accumulated: timedelta = field(default_factory=timedelta)
    input_mode: InputMode = InputMode.FREE
    preset_options: list[timedelta] = field(default_factory=list)
    user_defined_target: bool = False   # True when template said "free"
    _timer_start: Optional[datetime] = field(default=None, init=False, repr=False)

    def progress(self) -> float:
        return min(self.accumulated / self.target_duration, 1.0) if self.target_duration else 0.0

    def set_target(self, duration: timedelta):
        if not self.user_defined_target:
            raise ValueError("This goal's target is fixed by its template, not user-settable")
        self.target_duration = duration

    def log(self, duration: timedelta):
        if self.input_mode == InputMode.PRESET and duration not in self.preset_options:
            raise ValueError(f"{duration} is not one of the preset options {self.preset_options}")
        self.accumulated += duration
        self.refresh_status()

    def start_timer(self):
        if self.input_mode != InputMode.TIMER:
            raise ValueError("This goal isn't configured for timer input")
        self._timer_start = datetime.now()

    def stop_timer(self):
        if self._timer_start is None:
            raise ValueError("Timer wasn't running")
        self.accumulated += datetime.now() - self._timer_start
        self._timer_start = None
        self.refresh_status()


# ---------- Period wrappers ----------

@dataclass
class DailyGoal:
    goal: Goal
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        self.assigned_time = datetime.combine(today, time.min)
        self.finish_time = datetime.combine(today, time.max)

    def time_left_fraction(self) -> float:
        total = (self.finish_time - self.assigned_time).total_seconds()
        left = (self.finish_time - datetime.now()).total_seconds()
        return max(0.0, min(left / total, 1.0)) if total else 0.0


@dataclass
class WeeklyGoal:
    goal: Goal
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        self.assigned_time = datetime.combine(start, time.min)
        self.finish_time = datetime.combine(end, time.max)

    def time_left_fraction(self) -> float:
        total = (self.finish_time - self.assigned_time).total_seconds()
        left = (self.finish_time - datetime.now()).total_seconds()
        return max(0.0, min(left / total, 1.0)) if total else 0.0


@dataclass
class MonthlyGoal:
    goal: Goal
    assigned_time: datetime = field(init=False)
    finish_time: datetime = field(init=False)

    def __post_init__(self):
        today = datetime.now().date()
        start = today.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
        self.assigned_time = datetime.combine(start, time.min)
        self.finish_time = datetime.combine(end, time.max)

    def time_left_fraction(self) -> float:
        total = (self.finish_time - self.assigned_time).total_seconds()
        left = (self.finish_time - datetime.now()).total_seconds()
        return max(0.0, min(left / total, 1.0)) if total else 0.0


@dataclass
class CustomGoal:
    goal: Goal
    assigned_time: datetime
    finish_time: datetime

    def time_left_fraction(self) -> float:
        total = (self.finish_time - self.assigned_time).total_seconds()
        left = (self.finish_time - datetime.now()).total_seconds()
        return max(0.0, min(left / total, 1.0)) if total else 0.0