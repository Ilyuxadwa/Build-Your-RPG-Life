from datetime import date
import utils
import info
import healthy_calculations
from player import Player
from user import User
import register_manager

tasks = {"group": {"name": {"option1": {"time_delay", "bonuses"}}} ,"group2": {"name": {"option1": {"time_delay", "bonuses"}}}, "group3": {"name": {"option1": {"time_delay", "bonuses"}}}}
tasks_cooldown = {} # {name: time_left}

action_goals = []
amount_goals = []
time_goals = []

player = None



async def start(app):
    global player
    global action_goals, amount_goals, time_goals

    registered = await app.load("registered")
    require_new_fields = utils.check_registration(await app.load("registered_version"))

    if registered and not require_new_fields:
        user_data = utils.get_dict(await app.load("reg_data"))
        raw_daily_goals = utils.get_dict(await app.load("daily_goals"))
        raw_weekly_goals = utils.get_dict(await app.load("weekly_goals"))
        raw_custom_goals = utils.get_dict(await app.load("custom_goals"))
        
        user = User(user_data["name"], date.fromisoformat(user_data["birthday"]), user_data["role"], user_data["status"], user_data["weight"], user_data["height"], user_data["gender"], user_data["lifestyle_activeness"], user_data["preferences"], user_data["skills"])
        
        action_goals, amount_goals, time_goals = utils.parse_goals(user.role, user.status)

        goals = utils.load_goals_progress(raw_daily_goals, raw_weekly_goals, raw_custom_goals)

        player = Player(user) #goals[0], goals[1], goals[2], [])
        #player.start(...)

        #app.navigate("main_page")
        
    elif registered and require_new_fields:
        app.navigate("register_1")
        
    else:
        await app.save("registered", False)
        app.navigate("register_1")

async def set_player(app):
    pass

async def finish_registration(app):
    user_data = register_manager.finish()
    await app.save("reg_data", utils.save_dict(user_data))
    await app.save("registered", True)
    await app.save("registered_version", info.VERSION)
    app.navigate("register_1")


def load_tasks():
    global tasks
    tasks = utils.parse_tasks()