import utils

name = ""
birthday = utils.get_latest()
role = ""
status = ""

height = 0
weight = 0.0
gender = ""

def set_first_part(name_input, birthday_input, role_input, status_input):
    global name, birthday, role, status
    name = name_input
    birthday = birthday_input
    role = role_input
    status = status_input

def get_first_part():
    return name, birthday, role, status

def set_second_part(height_input, weight_input, gender_input):
    global height, weight, gender
    height = height_input
    weight = weight_input
    gender = gender_input

def get_second_part():
    return height, weight, gender