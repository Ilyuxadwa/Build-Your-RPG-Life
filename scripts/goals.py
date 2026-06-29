from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class AmountGoal:
    pass

@dataclass
class Goal():
    assigned_time: datetime
    finish_time: datetime

@dataclass
class DailyGoal(Goal):
    pass

@dataclass
class WeeklyGoal(Goal):
    pass

@dataclass
class CustomGoal(Goal):
    pass

