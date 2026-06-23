import utils

health = 100
creativity=0
intelligence=0

social=0
mood = 100
strength=0
energy=0

experience = 100
level = 1
skills = []


tasks = {} # {group: {name: {option1: {time_delay, bonuses}}}}}
already_done = {} # {name: time_left}

async def start(app):
    pass

def load_tasks():
    utils.parse_data()