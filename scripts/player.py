from dataclasses import dataclass
from user import User
from goals import DailyGoal, WeeklyGoal, CustomGoal
from tasks import Task, ActionTask, AmountTask, TimeTask
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

    energy = 50 # Gain/lose by actions
    mood = 50 # Gain/lose by actions
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

    def action_task(self, task, additional_option = []):
        final_stats = {
            "experience": 0,
            "creativity": 0,
            "intelligence": 0,
            "social": 0,
            "strength": 0,
            "mood": 0,
            "energy": 0,
            "stress": 0
        }

        if isinstance(task, ActionTask):
            for stat in task.stats.keys():
                final_stats[stat] += task.stats[stat]

            for option in additional_option or []:
                for stat in task.stats.keys():
                    final_stats[stat] += option.get(stat, 0)

            for multiplier in self.multipliers.keys():
                final_stats[multiplier] *= self.multipliers[multiplier]

        self.complete_new_stats(final_stats)
        return final_stats

    def amount_task(self, task, amount, additional_option = []):
            final_stats = {
                "experience": 0,
                "creativity": 0,
                "intelligence": 0,
                "social": 0,
                "strength": 0,
                "mood": 0,
                "energy": 0,
                "stress": 0
            }
    
            if isinstance(task, AmountTask):
                if task.amount_input_mode == "free":
                    for stat in final_stats.keys():
                        final_stats[stat] += task.amount_inputs_multipliers.keys()[0][stat] * (amount/int(task.amount_inputs_multipliers.keys()[0]))

                    for option in additional_option or []:
                        for stat in final_stats.keys():
                            final_stats[stat] += option.get(stat, 0) * (amount/int(task.amount_inputs_multipliers.keys()[0]))

                    for multiplier in self.multipliers.keys():
                        final_stats[multiplier] *= self.multipliers[multiplier]
                        
            self.complete_new_stats(final_stats)
            return final_stats

    def complete_new_stats(self, stats):
        self.add_experience(stats["experience"])
        self.creativity += stats["creativity"]
        self.intelligence += stats["intelligence"]
        self.social += stats["social"]
        self.strength += stats["strength"]
        self.mood += stats["mood"]
        self.energy += stats["energy"]
        self.stress += stats["stress"]

    def add_experience(self, exp):
        if utils.get_required_exp(self.level+1)<=self.experience+exp:
            self.level += 1
            self.experience = self.experience + exp - utils.get_required_exp(self.level)
        else:
            self.experience += exp        

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

    def calculate_multipliers(self):
        by_prefs, by_skills, by_roles, by_statuses = utils.get_affinities(self.user.status, self.user.role, self.user.preferences, self.user.skills)

        for multiplier in self.multipliers.keys():
            self.multipliers[multiplier] = 1 + (((by_prefs[multiplier] + by_skills[multiplier]) * 0.01) * ((by_roles[multiplier] + by_statuses[multiplier]) * 0.1))