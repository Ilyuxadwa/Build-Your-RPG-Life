from datetime import date

import utils
import info
from player import Player
from user import User
import register_manager



# ---------- App context ----------

current_path = ""
last_completed = {}
active_goal_time_refs = []
open_goal = None

tasks = {}
tasks_cooldown = {}

action_goals = []
amount_goals = []
time_goals = []

achievements = {}
achievement_progress = {}

water_history = {}
sleep_history = {}

player = None



# ---------- Start everything ----------

def start_parser():
    global tasks
    global achievements
    tasks = utils.parse_tasks()
    achievements = utils.parse_achievements()


async def start(app):
    global player, water_history, sleep_history, achievement_progress
    global action_goals, amount_goals, time_goals

    registered = await app.load("registered")
    require_new_fields = utils.check_registration(await app.load("registered_version"))

    if registered and not require_new_fields:
        user_data = utils.get_dict(await app.load("reg_data"))

        raw_daily_goals = utils.get_dict(await app.load("daily_goals"))
        raw_weekly_goals = utils.get_dict(await app.load("weekly_goals"))
        raw_custom_goals = utils.get_dict(await app.load("custom_goals"))
        raw_active_goals = utils.get_dict(await app.load("active_goals"))

        raw_achievements_progress = utils.get_dict(await app.load("achievements_progress"))
        if raw_achievements_progress:
            achievement_progress = raw_achievements_progress.get("progress", {})
            gained_achievements = raw_achievements_progress.get("completed", [])
        else:
            achievement_progress = {}
            gained_achievements = []

        user = User(user_data["name"], date.fromisoformat(user_data["birthday"]), user_data["role"], user_data["status"], user_data["weight"], user_data["height"], user_data["gender"], user_data["lifestyle_activeness"], user_data["preferences"], user_data["skills"], water_history, sleep_history)

        action_goals, amount_goals, time_goals = utils.parse_goals(user.role, user.status)

        daily_goals, weekly_goals, custom_goals = utils.load_goals_progress(raw_active_goals, raw_daily_goals, raw_weekly_goals, raw_custom_goals, action_goals, amount_goals, time_goals, user)

        stats = utils.get_dict(await app.load("statistics"))
        if not stats:
            stats = utils.get_initial_stats()

        player = Player(user, daily_goals, weekly_goals, custom_goals, gained_achievements)

        raw_water_history = utils.get_dict(await app.load("water_history"))
        water_history = raw_water_history if raw_water_history else {}

        raw_sleep_history = utils.get_dict(await app.load("sleep_history"))
        sleep_history = raw_sleep_history if raw_sleep_history else {}

        changed = utils.check_and_reset_goals(player, user)
        if changed:
            await save_goals(app)
        utils.refresh_system_goal_targets(player, user)
        
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

    

# ---------- Savers ----------

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


async def save_goals(app):
    global player, water_history, sleep_history

    d_goals, w_goals, c_goals = utils.save_goals_progress(player.daily_goals, player.weekly_goals, player.custom_goals)
    active_goals = utils.save_active_goals_progress(player.daily_goals, player.weekly_goals, player.custom_goals)

    water_history = utils.update_water_history(water_history, player)
    sleep_history = utils.update_sleep_history(sleep_history, player)

    await app.save("daily_goals", utils.save_dict(d_goals))
    await app.save("weekly_goals", utils.save_dict(w_goals))
    await app.save("custom_goals", utils.save_dict(c_goals))
    await app.save("active_goals", utils.save_dict(active_goals))
    await app.save("water_history", utils.save_dict(water_history))
    await app.save("sleep_history", utils.save_dict(sleep_history))



async def check_and_save_achievement(app, task_ref):
    global player, achievement_progress, achievements
    changed = False
    for ach_id, ach in achievements.items():
        if ach.reference_task != task_ref:
            continue
        if ach_id in player.achievements:
            continue

        achievement_progress[ach_id] = achievement_progress.get(ach_id, 0) + 1
        changed = True

        if achievement_progress[ach_id] >= ach.number:
            player.achievements.append(ach_id)

    if changed:
        await save_achievements(app)


async def save_achievements(app):
    global player, achievement_progress
    data = {
        "progress": achievement_progress,
        "completed": player.achievements,
    }
    await app.save("achievements_progress", utils.save_dict(data))