from dataclasses import dataclass
from user import User
from challanges import DailyChallange, WeeklyChallange, CustomChallange
from achievements import Achievement

@dataclass
class Player:

    user: User
    
    daily_challanges: list[DailyChallange]
    weekly_challanges: list[WeeklyChallange]
    custom_goals: list[CustomChallange]

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

