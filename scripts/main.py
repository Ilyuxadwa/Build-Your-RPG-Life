import utils
import healthy_calculations
from player import Player

user = Player()

tasks = {} # {group: {name: {option1: {time_delay, bonuses}}}}}
already_done = {} # {name: time_left}

async def start(app):
    pass

def load_tasks():
    utils.parse_data()