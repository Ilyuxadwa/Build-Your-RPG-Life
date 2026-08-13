from dataclasses import dataclass
from datetime import datetime, date

import healthy_calculations

@dataclass
class User:
    name: str
    birthday: date
    role: str
    status: str
    weight: float
    height: int
    gender: str
    lifestyle_activeness: int
    preferences: list
    skills: list

    def get_age(self):
        today = date.today()
        has_not_had_birthday_yet = (today.month, today.day) < (self.birthday.month, self.birthday.day)
        
        return int(today.year - self.birthday.year - has_not_had_birthday_yet)
    
    def weight_info(self):
        return healthy_calculations.bmi(self.weight, self.height, self.get_age(), self.gender)
    
    def initial_water_info(self):
        return healthy_calculations.water(self.weight, self.get_age(), self.gender)
    
    def sleep_info(self):
        return healthy_calculations.sleep(self.get_age())