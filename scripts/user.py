from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class User:
    name: str
    birthday: date
    weight: float
    height: int
    gender: str
    role: str
    lifestyle_activeness: int
    status: str
    preferences: dict
    skills: dict

    def get_age(self):
        today = date.today()
        has_not_had_birthday_yet = (today.month, today.day) < (self.birthday.month, self.birthday.day)
        
        return today.year - self.birthday.year - has_not_had_birthday_yet