from datetime import date

name = ""
birthday = date(1999, 12, 31)

height = 0
weight = 0.0
gender = ""

def set_first_part(name_input, birthday_input):
    global name, birthday
    name = name_input
    birthday = birthday_input

def get_first_part():
    return name, birthday


def set_second_part(height_input, weight_input, gender_input):
    global height, weight, gender
    height = height_input
    weight = weight_input
    gender = gender_input

def get_second_part():
    return height, weight, gender