from packaging.version import Version
from datetime import datetime, date, timedelta
from flet import Icons
import json
import os
import random
import copy

from goals import ActionGoal, AmountGoal, TimeGoal, DailyGoal, WeeklyGoal, CustomGoal, InputMode, GoalStatus
from tasks import ActionTask, AmountTask, TimeTask
from achievements import Achievement


STAT_KEYS = ["creativity", "intelligence", "social", "strength", "mood", "energy", "stress"]


def load_json(path, encoding=None):
    with open(path, "r", encoding=encoding) as f:
        return json.load(f)


icon_map = load_json("config/icons.json", encoding="utf-8")
welcome_messages = load_json("config/welcome_messages.json", encoding="utf-8")



# ---------- Parsers ----------

def parse_task_file(path):
    data = load_json(path, encoding="utf-8")

    common = {
        "title": data["title"],
        "description": data["description"],
        "cooldown_type": data["cooldown_type"],
        "cooldown": data["cooldown"],
        "available_for": data["available_for"],
        "recommended_for": data["recommended_for"],
        "additional_options_type": data["additional_options_type"],
        "additional_options_select": data["additional_options_select"],
        "additional_options": data["additional_options"],
    }

    task_type = data["type"]
    if task_type == "action":
        task = ActionTask(**common, stats=data["stats"])
    elif task_type == "amount":
        task = AmountTask(
            **common,
            units=data["units"],
            amount_input_mode=data["amount_input_mode"],
            min=data["min"],
            max=data["max"],
            step=data.get("step", 1),
            amount_inputs_multipliers=data["amount_inputs_multipliers"]
        )
    elif task_type == "time":
        task = TimeTask(
            **common,
            time_input=data["time_input"],
            min=data["min"],
            max=data["max"],
            step=data.get("step", 10),
            time_inputs_multipliers=data["time_inputs_multipliers"]
        )
    else:
        raise ValueError(f"Unknown task type: {task_type}")

    return data["id"], task


def parse_tasks(path="content/tasks/"):
    parsed = {}
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            parsed[name] = parse_tasks(full_path)
        elif name.endswith(".json"):
            task_id, task = parse_task_file(full_path)
            parsed[task_id] = task
    return parsed


def get_node(path, tasks):
    node = tasks
    for part in path.split("/"):
        node = node[part]
    return node



def parse_achievement_file(path):
    data = load_json(path, encoding="utf-8")

    achievement = Achievement(
        message=data["message"],
        task=data["task"],
        number=data["number"],
        reference_task=data["ref_task"],
    )

    return data["id"], achievement


def parse_achievements(path="content/achievements/"):
    parsed = {}
    for name in os.listdir(path):
        if name.endswith(".json"):
            full_path = os.path.join(path, name)
            achievement_id, achievement = parse_achievement_file(full_path)
            parsed[achievement_id] = achievement
    return parsed



def is_available_for(raw_data, role, status):
    return role in raw_data["available_for"] and status in raw_data["available_for"]


def available_periods_dict(raw_data):
    return {
        "daily": raw_data.get("is_daily", False),
        "weekly": raw_data.get("is_weekly", False),
        "custom": raw_data.get("is_custom", False),
    }


def parse_goals(role, status):
    actions = os.listdir("content/goals/action/")
    amounts = os.listdir("content/goals/amount/")
    times = os.listdir("content/goals/time/")

    action_goals = []
    amount_goals = []
    time_goals = []

    for goal in actions:
        raw_data = load_json("content/goals/action/" + goal, encoding="utf-8")

        if not is_available_for(raw_data, role, status):
            continue

        action_goals.append(ActionGoal(
            title=raw_data["title"],
            description=raw_data["description"],
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods=available_periods_dict(raw_data),
        ))

    for goal in amounts:
        raw_data = load_json("content/goals/amount/" + goal, encoding="utf-8")

        if not is_available_for(raw_data, role, status):
            continue

        amount_goals.append(AmountGoal(
            title=raw_data["title"],
            description=raw_data["description"],
            target_amount=raw_data["target"],
            unit=raw_data.get("units", ""),
            input_mode=parse_input_mode(raw_data["input_mode"]),
            step=raw_data.get("step", 1),
            preset_options=raw_data.get("input_options", []),
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods=available_periods_dict(raw_data),
        ))

    for goal in times:
        raw_data = load_json("content/goals/time/" + goal, encoding="utf-8")

        if not is_available_for(raw_data, role, status):
            continue

        target = raw_data["target"]
        if target == "free":
            target_duration = timedelta()
            user_defined_target = True
        else:
            h, m, s = (int(x) for x in target.split(":"))
            target_duration = timedelta(hours=h, minutes=m, seconds=s)
            user_defined_target = False

        time_goals.append(TimeGoal(
            title=raw_data["title"],
            description=raw_data["description"],
            target_duration=target_duration,
            user_defined_target=user_defined_target,
            input_mode=parse_input_mode(raw_data["input_mode"]),
            step=raw_data.get("step", 10),
            preset_options=raw_data.get("input_options", []),
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods=available_periods_dict(raw_data),
        ))

    return action_goals, amount_goals, time_goals


def parse_input_mode(raw_value: str) -> InputMode:
    normalized = raw_value.strip().lower()

    if normalized in ("free", "freeform", "free_form", "manual"):
        return InputMode.FREE
    if normalized in ("preset", "presets", "fixed", "options"):
        return InputMode.PRESET
    if normalized in ("timer", "stopwatch"):
        return InputMode.TIMER

    raise ValueError(f"Unknown input_mode value: {raw_value!r}")


def goal_progress_entry(goal):
    common = {
        "status": goal.status.value,
        "already_completed": goal.already_completed,
        "date": date.today().isoformat(),
    }

    if isinstance(goal, ActionGoal):
        return {"type": "action", "completed": goal.done, **common}
    elif isinstance(goal, AmountGoal):
        return {"type": "amount", "current": goal.current_amount,
                "completed": goal.is_complete(), **common}
    elif isinstance(goal, TimeGoal):
        return {"type": "time", "current": goal.accumulated.total_seconds(),
                "completed": goal.is_complete(), **common}


def goals_progress_dict(period_goals):
    return {period_goal.goal.title: goal_progress_entry(period_goal.goal) for period_goal in period_goals}


def save_goals_progress(daily: list, weekly: list, custom: list):
    return goals_progress_dict(daily), goals_progress_dict(weekly), goals_progress_dict(custom)


def active_goal_entry(period_goal, period_label):
    return {
        "period": period_label,
        "assigned_time": period_goal.assigned_time.isoformat(),
        "finish_time": period_goal.finish_time.isoformat(),
    }


def save_active_goals_progress(daily: list, weekly: list, custom: list):
    active_dict = {}

    for period_goals, period_label in ((daily, "daily"), (weekly, "weekly"), (custom, "custom")):
        for period_goal in period_goals:
            active_dict[period_goal.goal.title] = active_goal_entry(period_goal, period_label)

    return active_dict


def find_system_goal(player, title):
    return next((pg.goal for pg in player.daily_goals if pg.goal.is_system and pg.goal.title == title), None)


def update_water_history(history: dict, player):
    today = date.today().isoformat()

    water_goal = find_system_goal(player, "Drinking water")

    if water_goal is not None and water_goal.current_amount > 0:
        history[today] = water_goal.current_amount

    return history


def update_sleep_history(history: dict, player):
    today = date.today().isoformat()

    sleep_goal = find_system_goal(player, "Sleeping")

    if sleep_goal is not None and sleep_goal.accumulated.total_seconds() > 0:
        history[today] = sleep_goal.accumulated.total_seconds() / 60

    return history


def find_in_pool(title, action_goals, amount_goals, time_goals):
    for g in action_goals:
        if g.title == title:
            return g
    for g in amount_goals:
        if g.title == title:
            return g
    for g in time_goals:
        if g.title == title:
            return g
    return None


def apply_progress(goal, progress):
    if not progress:
        return
    if isinstance(goal, ActionGoal):
        goal.done = progress.get("completed", False)
    elif isinstance(goal, AmountGoal):
        goal.current_amount = progress.get("current", 0.0)
    elif isinstance(goal, TimeGoal):
        goal.accumulated = timedelta(seconds=progress.get("current", 0))
    goal.status = GoalStatus(progress.get("status", "in_progress"))
    goal.already_completed = progress.get("already_completed", False)


def apply_progress_if_today(goal, progress):
    if not progress:
        return
    if progress.get("date") != date.today().isoformat():
        return
    apply_progress(goal, progress)


def reset_progress_fields(goal):
    if isinstance(goal, ActionGoal):
        goal.done = False
    elif isinstance(goal, AmountGoal):
        goal.current_amount = 0.0
    elif isinstance(goal, TimeGoal):
        goal.accumulated = timedelta()
    goal.status = GoalStatus.IN_PROGRESS


def reset_progress(goal):
    reset_progress_fields(goal)
    goal.already_completed = False


def load_goals_progress(active: dict, daily: dict, weekly: dict, custom: dict,
                          action_goals: list, amount_goals: list, time_goals: list,
                          user):
    daily_goals = []
    weekly_goals = []
    custom_goals = []

    for title, info in active.items():
        template = find_in_pool(title, action_goals, amount_goals, time_goals)
        if template is None:
            continue  # system goals are handled separately below, never come from the pool

        goal = copy.deepcopy(template)
        period = info["period"]

        if period == "daily":
            apply_progress(goal, daily.get(title))
            finish_time = datetime.fromisoformat(info["finish_time"])
            if datetime.now() > finish_time:
                reset_progress(goal)
                daily_goals.append(DailyGoal(goal=goal))
            else:
                wrapped = DailyGoal(goal=goal)
                wrapped.assigned_time = datetime.fromisoformat(info["assigned_time"])
                wrapped.finish_time = finish_time
                daily_goals.append(wrapped)

        elif period == "weekly":
            apply_progress(goal, weekly.get(title))
            finish_time = datetime.fromisoformat(info["finish_time"])
            if datetime.now() > finish_time:
                reset_progress(goal)
                weekly_goals.append(WeeklyGoal(goal=goal))
            else:
                wrapped = WeeklyGoal(goal=goal)
                wrapped.assigned_time = datetime.fromisoformat(info["assigned_time"])
                wrapped.finish_time = finish_time
                weekly_goals.append(wrapped)

        elif period == "custom":
            apply_progress(goal, custom.get(title))
            custom_goals.append(CustomGoal(
                goal=goal,
                assigned_time=datetime.fromisoformat(info["assigned_time"]),
                finish_time=datetime.fromisoformat(info["finish_time"]),
            ))

    water_wrapped = make_water_goal(user)
    apply_progress_if_today(water_wrapped.goal, daily.get(water_wrapped.goal.title))
    daily_goals.append(water_wrapped)

    sleep_wrapped = make_sleep_goal(user)
    apply_progress_if_today(sleep_wrapped.goal, daily.get(sleep_wrapped.goal.title))
    daily_goals.append(sleep_wrapped)

    return daily_goals, weekly_goals, custom_goals


def make_water_goal(user):
    goal = AmountGoal(
        title="Drinking water",
        description="Water - is the basic component of your life.",
        target_amount=user.initial_water_info(),
        unit="ml",
        step=50,
        is_system=True,
        available_periods={"daily": True, "weekly": False, "custom": False},
        stats={
            "experience": 30,
            "creativity": 0,
            "intelligence": 0,
            "social": 0,
            "strength": 0,
            "mood": 10,
            "energy": 10,
            "stress": -5,
        },
    )
    return DailyGoal(goal=goal)


def make_sleep_goal(user) -> DailyGoal:
    sleep_info = user.sleep_info()

    goal = TimeGoal(
        title="Sleeping",
        description="Sleep is a key for wellness",
        target_duration=timedelta(minutes=sleep_info["target_minutes"]),
        is_system=True,
        step=900,
        user_defined_target=False,
        available_periods={"daily": True, "weekly": False, "custom": False},
        stats={
            "experience": 35,
            "creativity": 0,
            "intelligence": 0,
            "social": 0,
            "strength": 0,
            "mood": 15,
            "energy": 50,
            "stress": -20,
        },
    )
    return DailyGoal(goal=goal)


def refresh_system_goal_target(goal, user):
    if goal.is_system and goal.title == "Drinking water":
        goal.target_amount = user.initial_water_info()
    elif goal.is_system and goal.title == "Sleeping":
        goal.target_duration = timedelta(minutes=user.sleep_info()["target_minutes"])


def refresh_system_goal_targets(player, user):
    for pg in player.daily_goals:
        refresh_system_goal_target(pg.goal, user)


def reset_goal_progress(goal):
    reset_progress_fields(goal)


def check_and_reset_goals(player, user):
    changed = False

    for i, pg in enumerate(player.daily_goals):
        if datetime.now() > pg.finish_time:
            reset_goal_progress(pg.goal)
            refresh_system_goal_target(pg.goal, user)

            player.daily_goals[i] = DailyGoal(goal=pg.goal)
            changed = True

    for i, pg in enumerate(player.weekly_goals):
        if datetime.now() > pg.finish_time:
            reset_goal_progress(pg.goal)
            player.weekly_goals[i] = WeeklyGoal(goal=pg.goal)
            changed = True

    return changed



# ---------- Config things ----------

def get_initial_stats():
    return load_json("config/initial.json")

def get_roles():
    return load_json("config/roles.json")

def get_statuses():
    return load_json("config/statuses.json")

def get_available_skills():
    return load_json("config/skills.json")

def get_available_preferences():
    return load_json("config/preferences.json")

def get_affinities(status, role, prefs, skills):
    global_prefs = get_available_preferences()
    global_skills = get_available_skills()
    global_statuses = get_statuses()
    global_roles = get_roles()

    prefs_affinity = {stat: 0 for stat in STAT_KEYS}
    for pref in prefs:
        for stat in STAT_KEYS:
            prefs_affinity[stat] += global_prefs[pref]["affinity"][stat]

    skills_affinity = {stat: 0 for stat in STAT_KEYS}
    for skill in skills:
        for stat in STAT_KEYS:
            skills_affinity[stat] += global_skills[skill]["affinity"][stat]

    roles_multiplier = {stat: global_roles[role][stat] for stat in STAT_KEYS}
    statuses_multiplier = {stat: global_statuses[status][stat] for stat in STAT_KEYS}

    return prefs_affinity, skills_affinity, roles_multiplier, statuses_multiplier


def icon(name: str):
    icon_key = icon_map.get(name)
    if icon_key is None:
        raise KeyError(f"No icon mapped for '{name}'")
    icon_value = getattr(Icons, icon_key, None)
    if icon_value is None:
        raise AttributeError(f"ft.Icons has no attribute '{icon_key}'")
    return icon_value


def welcome_message(user):
    if user.birthday == date.today():
        return icon("welcome-birthday"), f"Happy birthday, {user.name}!"
    else:
        msg = random.choice(list(welcome_messages))
        return icon("welcome-"+welcome_messages.get(msg)), msg.replace("{name}", user.name)



# ---------- Main logic ----------

def save_dict(value):
    return json.dumps(value)


def get_dict(raw):
    default={}
    if raw:
        return json.loads(raw)
    return default


def check_registration(version):
    if version is None:
        return True
    version = Version(version)
    data = load_json("config/register_fields.json")
    for ver in data.keys():
        if version < Version(ver):
            return True
    return False



# ---------- Checkers and transformers ----------

def get_latest():
    return date(date.today().year-12, date.today().month, date.today().day)

def get_earliest():
    return date(date.today().year-100, date.today().month, date.today().day)

def to_seconds(time_str: str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def seconds_until(finish_time):
    return (finish_time - datetime.now()).total_seconds()

def format_time_left_days(finish_time):
    seconds = seconds_until(finish_time)
    if seconds <= 0:
        return "Time left: 0:00:00:00"

    total_seconds = int(seconds)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"Time left: {days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_time_left_hours(finish_time):
    seconds = seconds_until(finish_time)
    if seconds <= 0:
        return "Time left: 0:00:00:00"

    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"Time left: {hours:02d}:{minutes:02d}:{seconds:02d}"

def parse_time_string(duration: str) -> timedelta:
    h, m, s = (int(x) for x in duration.split(":"))
    return timedelta(hours=h, minutes=m, seconds=s)

def add_time(current_time, max_time, step):
    t = datetime.strptime(current_time, "%H:%M:%S") + timedelta(seconds=step)
    maximum = datetime.strptime(max_time, "%H:%M:%S")
    if t > maximum:
        result = current_time
    else:
        result = t.strftime("%H:%M:%S")
    return result

def remove_time(current_time, min_time, step):
    t = datetime.strptime(current_time, "%H:%M:%S") - timedelta(seconds=step)
    minimum = datetime.strptime(min_time, "%H:%M:%S")
    if t < minimum:
        result = current_time
    else:
        result = t.strftime("%H:%M:%S")
    return result

def get_required_exp(level):
    levels = load_json("config/levels.json")
    return levels[str(level)]

def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))