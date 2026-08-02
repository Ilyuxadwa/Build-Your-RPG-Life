from datetime import date
import utils
import info
import healthy_calculations
from player import Player
from user import User
import register_manager

current_path = ""
last_completed = {}

tasks = {}
tasks_cooldown = {}

action_goals = []
amount_goals = []
time_goals = []

achievements = {}

player = None



def start_parser():
    global tasks
    global achievements
    tasks = utils.parse_tasks()
    achievements = utils.parse_achievements()

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
        raw_active_goals = await app.load("active_goals")

        gained_achievements = await app.load("gained_achievements")
        
        user = User(user_data["name"], date.fromisoformat(user_data["birthday"]), user_data["role"], user_data["status"], user_data["weight"], user_data["height"], user_data["gender"], user_data["lifestyle_activeness"], user_data["preferences"], user_data["skills"])

        action_goals, amount_goals, time_goals = utils.parse_goals(user.role, user.status)

        goals_progress = utils.load_goals_progress(raw_daily_goals, raw_weekly_goals, raw_custom_goals)
        #active_goals = utils.load_active_goals()

        stats = utils.get_dict(await app.load("statistics"))
        if not stats:
            stats = utils.get_initial_stats()

        player = Player(user, gained_achievements)
        player.start(stats)

        app.navigate("main_page")
        
    elif registered and require_new_fields:
        app.navigate("register_1")
        
    else:
        await app.save("registered", False)
        app.navigate("register_1")

async def finish_registration(app):
    user_data = register_manager.finish()
    await app.save("reg_data", utils.save_dict(user_data))
    await app.save("registered", True)
    await app.save("registered_version", info.VERSION)
    await start(app)

async def save_stats(app):
    global player
    await app.save("statistics", utils.save_dict(
        {
            "exp": player.experience,
            "level": player.level,
            "health": player.health,
            "creativity": player.creativity,
            "intelligence": player.intelligence,
            "social": player.social,
            "strength": player.strength,
            "mood": player.mood,
            "energy": player.energy,
            "stress": player.stress
        }
    ))