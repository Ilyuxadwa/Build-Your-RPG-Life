import utils
import healthy_calculations
from player import Player

tasks = {"group": {"name": {"option1": {"time_delay", "bonuses"}}} ,"group2": {"name": {"option1": {"time_delay", "bonuses"}}}, "group3": {"name": {"option1": {"time_delay", "bonuses"}}}}
already_done = {} # {name: time_left}

async def start(app):
    registered = await app.load("registered")
    if registered:
        pass
    else:
        await app.save("registerd", False)
        app.navigate("register_1")


def load_tasks():
    global tasks
    tasks = utils.parse_tasks()