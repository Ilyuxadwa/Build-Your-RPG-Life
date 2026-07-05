from dataclasses import dataclass
from datetime import datetime, date

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
        
        return today.year - self.birthday.year - has_not_had_birthday_yet