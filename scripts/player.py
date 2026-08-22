from datetime import date, timedelta
from dataclasses import dataclass

import utils
from user import User
from goals import DailyGoal, WeeklyGoal, CustomGoal, ActionGoal, AmountGoal, TimeGoal, GoalStatus
from tasks import ActionTask, AmountTask, TimeTask



@dataclass
class Player:

    # ---------- Essential parts ----------

    user: User
    
    daily_goals: list[DailyGoal]
    weekly_goals: list[WeeklyGoal]
    custom_goals: list[CustomGoal]

    achievements: list[str]


    # ---------- Statistics ----------

    experience = 0 # Changed by actions
    level = 1 # +1 when experience = required amount, experience = current + added - required

    health = 100 # Changed by a lot of factors

    creativity = 0 # Changed by actions
    intelligence = 0 # Changed by actions
    social = 0 # Changed by actions
    strength = 0 # Changed by actions

    energy = 50 # Changed by actions
    mood = 50 # Changed by actions
    stress = 0 # Changed by actions

    multipliers = { # Calculated on start
                "creativity": 1,
                "intelligence": 1,
                "social": 1,
                "strength": 1,
                "mood": 1,
                "energy": 1,
                "stress": 1
            }


    
    def start(self, saved_values):
            self.level = saved_values["level"]
            self.experience = saved_values["exp"]
    
            self.creativity = saved_values["creativity"]
            self.intelligence = saved_values["intelligence"]
            self.social = saved_values["social"]
            self.strength = saved_values["strength"]
    
            self.mood = saved_values["mood"]
            self.energy = saved_values["energy"]
            self.stress = saved_values["stress"]
    
            self.calculate_multipliers()
            self.update_health()



    # ---------- Actions completements ----------

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
                    final_stats[stat] += task.additional_options[option][stat]

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
                key = list(task.amount_inputs_multipliers.keys())[0]
                for stat in final_stats.keys():
                    final_stats[stat] += task.amount_inputs_multipliers[key][stat] * (amount/int(key))

                for option in additional_option or []:
                    for stat in final_stats.keys():
                        final_stats[stat] += task.additional_options[option][stat] * (amount/int(key))

            elif task.amount_input_mode == "preset":
                for stat in final_stats.keys():
                    final_stats[stat] += task.amount_inputs_multipliers[amount][stat]

                for option in additional_option or []:
                    for stat in final_stats.keys():
                        final_stats[stat] += task.additional_options[option][stat]

            for multiplier in self.multipliers.keys():
                final_stats[multiplier] *= self.multipliers[multiplier]

        self.complete_new_stats(final_stats)

        return final_stats


    def time_task(self, task, time: str, additional_option = []):
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

        if isinstance(task, TimeTask):
            if task.time_input == "free":
                time = utils.to_seconds(time)
                required = utils.to_seconds(list(task.time_inputs_multipliers.keys())[0])
                for stat in final_stats.keys():
                    final_stats[stat] += task.time_inputs_multipliers[list(task.time_inputs_multipliers.keys())[0]][stat] * (time/required)

                for option in additional_option or []:
                    for stat in final_stats.keys():
                        final_stats[stat] += task.additional_options[option][stat] * (time/required)

            elif task.time_input == "preset":
                for stat in final_stats.keys():
                    final_stats[stat] += task.time_inputs_multipliers[time][stat]

                for option in additional_option or []:
                    for stat in final_stats.keys():
                        final_stats[stat] += task.additional_options[option][stat]

            for multiplier in self.multipliers.keys():
                final_stats[multiplier] *= self.multipliers[multiplier]

        self.complete_new_stats(final_stats)
        
        return final_stats


    def complete_goal(self, goal, param: str = ""):
        if isinstance(goal.goal, ActionGoal):
            goal.goal.complete()
        elif isinstance(goal.goal, AmountGoal) or isinstance(goal.goal, TimeGoal):
            goal.goal.add_progress(param)
            
        if goal.goal.is_complete() and not goal.goal.already_completed:
            self.complete_new_stats(goal.goal.stats)
            goal.goal.already_completed = True
            return goal.goal.stats
        else:
            return False
            

        
    # ---------- Calculations ----------

    def complete_new_stats(self, stats):
        self.add_experience(stats["experience"])
        self.creativity = utils.clamp(self.creativity + stats["creativity"])
        self.intelligence = utils.clamp(self.intelligence + stats["intelligence"])
        self.social = utils.clamp(self.social + stats["social"])
        self.strength = utils.clamp(self.strength + stats["strength"])
        self.mood = utils.clamp(self.mood + stats["mood"])
        self.energy = utils.clamp(self.energy + stats["energy"])
        self.stress = utils.clamp(self.stress + stats["stress"])
        self.update_health()


    def add_experience(self, exp):
        if utils.get_required_exp(self.level+1)<=self.experience+exp:
            self.level += 1
            self.experience = self.experience + exp - utils.get_required_exp(self.level)
        else:
            self.experience += exp     


    def calculate_multipliers(self):
        by_prefs, by_skills, by_roles, by_statuses = utils.get_affinities(self.user.status, self.user.role, self.user.preferences, self.user.skills)

        for multiplier in self.multipliers.keys():
            self.multipliers[multiplier] = 1 + (((by_prefs[multiplier] + by_skills[multiplier]) * 0.01) * ((by_roles[multiplier] + by_statuses[multiplier]) * 0.1))


    def update_health(self):
        weight_info = self.user.weight_info()
        water_target_ml = self.user.initial_water_info()
        sleep_info = self.user.sleep_info()

        today = date.today()
        last_7_days = [today - timedelta(days=i) for i in range(7)]

        min_sleep_minutes = sleep_info["min_hours"] * 60
        max_sleep_minutes = sleep_info["max_hours"] * 60

        sleep_scores = []
        for day in last_7_days:
            day_key = day.isoformat()
            if day_key not in self.user.sleep_history:
                continue
            sleep_minutes = self.user.sleep_history[day_key]

            if sleep_minutes < min_sleep_minutes:
                score = (sleep_minutes / min_sleep_minutes) * 100
            elif sleep_minutes > max_sleep_minutes:
                over_minutes = sleep_minutes - max_sleep_minutes
                score = 100 - (over_minutes / 60) * 10
                if score < 0:
                    score = 0
            else:
                score = 100

            sleep_scores.append(score)

        if sleep_scores:
            avg_sleep_score = sum(sleep_scores) / len(sleep_scores)
        else:
            avg_sleep_score = 50

        water_scores = []
        for day in last_7_days:
            day_key = day.isoformat()
            if day_key not in self.user.water_history:
                continue
            water_ml = self.user.water_history[day_key]

            if water_ml < water_target_ml:
                score = (water_ml / water_target_ml) * 100
            elif water_ml <= water_target_ml * 1.5:
                score = 100
            else:
                over_ml = water_ml - (water_target_ml * 1.5)
                score = 100 - (over_ml / water_target_ml) * 100
                if score < 0:
                    score = 0

            water_scores.append(score)

        if water_scores:
            avg_water_score = sum(water_scores) / len(water_scores)
        else:
            avg_water_score = 50

        bmi_category = weight_info["health_category"]
        if bmi_category == "normal":
            bmi_score = 100
        elif bmi_category == "underweight":
            bmi_score = 60
        elif bmi_category == "overweight":
            bmi_score = 60
        elif bmi_category == "obese":
            bmi_score = 30
        else:
            bmi_score = 50

        stress_score = 100 - self.stress
        mood_score = self.mood
        energy_score = self.energy
        strength_score = self.strength

        health = (
            avg_sleep_score * 0.20
            + avg_water_score * 0.20
            + bmi_score * 0.20
            + stress_score * 0.10
            + mood_score * 0.10
            + energy_score * 0.10
            + strength_score * 0.10
        )

        if health < 0:
            health = 0
        elif health > 100:
            health = 100

        self.health = int(health)