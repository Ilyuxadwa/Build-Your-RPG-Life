from dataclasses import dataclass
from user import User
from goals import DailyGoal, WeeklyGoal, CustomGoal
from achievements import Achievement
import utils

@dataclass
class Player:

    user: User
    
    #daily_challenges: list[DailyGoal]
    #weekly_challenges: list[WeeklyGoal]
    #custom_goals: list[CustomGoal]

    #achievements: list[Achievement]

    # Stats
    experience = 0 # Gain/lose by actions
    level = 1 # When experience = required amount -> +1, experience = 0

    health = 100 # Calculated by a lot of factors

    creativity = 0 # Gain/lose by actions
    intelligence = 0 # Gain/lose by actions
    social = 0 # Gain/lose by actions
    strength = 0 # Gain/lose by actions

    mood = 50 # Gain/lose by actions
    energy = 50 # Gain/lose by actions
    stress = 0 # Gain/lose by actions

    multipliers={
                    "creativity": 1,
                    "intelligence": 1,
                    "social": 1,
                    "strength": 1,
                    "mood": 1,
                    "energy": 1,
                    "stress": 1
                }

    def add_experience(self, exp):
        if utils.get_required_exp(self.level+1)<=self.experience+exp:
            self.level += 1
            self.experience = self.experience + exp - utils.get_required_exp(self.level)
        else:
            self.experience += exp

    def action(self, name, additional_option = ""):
        pass

    def update_health(self):
        pass

    def start(self, saved_values):
        self.level = saved_values["level"]
        self.experience = saved_values["exp"]
        self.update_health()

        self.creativity = saved_values["creativity"]
        self.intelligence = saved_values["intelligence"]
        self.social = saved_values["social"]
        self.strength = saved_values["strength"]

        self.mood = saved_values["mood"]
        self.energy = saved_values["energy"]
        self.stress = saved_values["stress"]

        self.calculate_multipliers()

    def calculate_multipliers():
        pass