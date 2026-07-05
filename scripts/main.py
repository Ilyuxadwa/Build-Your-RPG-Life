import utils
import info
import healthy_calculations
from player import Player
from user import User
import register_manager

tasks = {"group": {"name": {"option1": {"time_delay", "bonuses"}}} ,"group2": {"name": {"option1": {"time_delay", "bonuses"}}}, "group3": {"name": {"option1": {"time_delay", "bonuses"}}}}
already_done = {} # {name: time_left}

user = None
player = None



async def start(app):
    global user
    registered = await app.load("registered")
    require_new_fields = utils.check_registration(await app.load("registered_version"))
    if registered and not require_new_fields:
        data = utils.get_dict(await app.load("reg_data"))
        user = User(data["name"], data["birthday"], data["role"], data["status"], data["weight"], data["height"], data["gender"], data["lifestyle_activeness"], data["preferences"], data["skills"])
    else:
        await app.save("registerd", False)
        app.navigate("register_1")

async def set_player(app):
    pass

async def finish_registration(app):
    user_data = register_manager.finish()
    app.save("reg_data", utils.save_dict(user_data))
    app.save("registered", True)
    app.save("registered_version", info.version)


def load_tasks():
    global tasks
    tasks = utils.parse_tasks()