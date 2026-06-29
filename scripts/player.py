from dataclasses import dataclass
from user import User
from goals import DailyGoal, WeeklyGoal, CustomGoal
from achievements import Achievement

@dataclass
class Player:

    user: User
    
    daily_challanges: list[DailyGoal]
    weekly_challanges: list[WeeklyGoal]
    custom_goals: list[CustomGoal]

    # Stats
    experience = 0 # Gain/lose by actions
    level = 1 # When experiece = required amount -> +1, experience = 0
    health = 100 # Calculated by a lot of factors
    creativity = 0 # Gain/lose by actions
    intelligence = 0 # Gain/lose by actions
    social = 0 # Gain/lose by actions
    strength = 0 # Gain/lose by actions

    mood = 50 # Gain/lose by actions
    energy = 50 # Gain/lose by actions
    stress = 0 # Gain/lose by actions
    
    achievements: list[Achievement]

    def get_age(self):
        return self.user.get_age()

