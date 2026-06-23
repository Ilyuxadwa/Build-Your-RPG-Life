from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Player:
    name: str # User name/nickname
    birthday: date # User birthday as date(1999, 12, 31)
    weight: float # Weight in kg
    height: int # height in cm
    gender: str # male/female
    role: str # Scholar/Student/Worker/None
    lifestyle_activeness: int # Range 0-100
    status: str # Alone/With partner/Married 
    preferences: dict #Chooseable (Reading, reading_genres as list, movies, movies_genres as list, )
    skills: dict #(Riding a bike, swimming, programming, )
    system_goals: dict #Drinking a water
    custom_goals: dict #Boolean or value, depends on task

    def get_age(self):
        today = date.today()
        has_not_had_birthday_yet = (today.month, today.day) < (self.birthday.month, self.birthday.day)
        
        return today.year - self.birthday.year - has_not_had_birthday_yet

