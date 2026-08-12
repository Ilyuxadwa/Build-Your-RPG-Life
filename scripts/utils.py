import json
import os
import random
import copy
from packaging.version import Version
from datetime import datetime, date, timedelta
from flet import Icons
from goals import ActionGoal, AmountGoal, TimeGoal, DailyGoal, WeeklyGoal, CustomGoal, InputMode, GoalStatus
from tasks import ActionTask, AmountTask, TimeTask
from achievements import Achievement



with open("config/icons.json", "r", encoding="utf-8") as f:
    icon_map = json.load(f)

with open("config/welcome_messages.json", "r", encoding="utf-8") as f:
    welcome_messages = json.load(f)



def parse_task_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

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
            amount_inputs_multipliers=data["amount_inputs_multipliers"],
        )
    elif task_type == "time":
        task = TimeTask(
            **common,
            time_input=data["time_input"],
            min=data["min"],
            max=data["max"],
            time_inputs_multipliers=data["time_inputs_multipliers"],
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
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

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


def parse_goals(role, status):
    actions = os.listdir("content/goals/action/")
    amounts = os.listdir("content/goals/amount/")
    times = os.listdir("content/goals/time/")

    action_goals = []
    amount_goals = []
    time_goals = []

    for goal in actions:
        with open("content/goals/action/" + goal, encoding="utf-8") as f:
            raw_data = json.load(f)

        if role not in raw_data["available_for"] or status not in raw_data["available_for"]:
            continue

        action_goals.append(ActionGoal(
            title=raw_data["title"],
            description=raw_data["description"],
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods={
                "daily": raw_data.get("is_daily", False),
                "weekly": raw_data.get("is_weekly", False),
                "custom": raw_data.get("is_custom", False),
            },
        ))

    for goal in amounts:
        with open("content/goals/amount/" + goal, encoding="utf-8") as f:
            raw_data = json.load(f)

        if role not in raw_data["available_for"] or status not in raw_data["available_for"]:
            continue

        amount_goals.append(AmountGoal(
            title=raw_data["title"],
            description=raw_data["description"],
            target_amount=raw_data["target"],
            unit=raw_data.get("units", ""),
            input_mode=parse_input_mode(raw_data["input_mode"]),
            preset_options=raw_data.get("input_options", []),
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods={
                "daily": raw_data.get("is_daily", False),
                "weekly": raw_data.get("is_weekly", False),
                "custom": raw_data.get("is_custom", False),
            },
        ))

    for goal in times:
        with open("content/goals/time/" + goal, encoding="utf-8") as f:
            raw_data = json.load(f)

        if role not in raw_data["available_for"] or status not in raw_data["available_for"]:
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
            preset_options=raw_data.get("input_options", []),
            stats=raw_data.get("stats", {}),
            additional_options=raw_data.get("additional_options", {}),
            recommended_for=raw_data.get("recommended_for", []),
            available_periods={
                "daily": raw_data.get("is_daily", False),
                "weekly": raw_data.get("is_weekly", False),
                "custom": raw_data.get("is_custom", False),
            },
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
    if isinstance(goal, ActionGoal):
        return {"type": "action", "completed": goal.done, "status": goal.status.value}
    elif isinstance(goal, AmountGoal):
        return {"type": "amount", "current": goal.current_amount,
                "completed": goal.is_complete(), "status": goal.status.value}
    elif isinstance(goal, TimeGoal):
        return {"type": "time", "current": goal.accumulated.total_seconds(),
                "completed": goal.is_complete(), "status": goal.status.value}


def save_goals_progress(daily: list, weekly: list, custom: list):
    daily_dict = {}
    for period_goal in daily:
        daily_dict[period_goal.goal.title] = goal_progress_entry(period_goal.goal)

    weekly_dict = {}
    for period_goal in weekly:
        weekly_dict[period_goal.goal.title] = goal_progress_entry(period_goal.goal)

    custom_dict = {}
    for period_goal in custom:
        custom_dict[period_goal.goal.title] = goal_progress_entry(period_goal.goal)

    return daily_dict, weekly_dict, custom_dict

def save_active_goals_progress(daily: list, weekly: list, custom: list):
    active_dict = {}

    for period_goal in daily:
        active_dict[period_goal.goal.title] = {
            "period": "daily",
            "assigned_time": period_goal.assigned_time.isoformat(),
            "finish_time": period_goal.finish_time.isoformat(),
        }

    for period_goal in weekly:
        active_dict[period_goal.goal.title] = {
            "period": "weekly",
            "assigned_time": period_goal.assigned_time.isoformat(),
            "finish_time": period_goal.finish_time.isoformat(),
        }

    for period_goal in custom:
        active_dict[period_goal.goal.title] = {
            "period": "custom",
            "assigned_time": period_goal.assigned_time.isoformat(),
            "finish_time": period_goal.finish_time.isoformat(),
        }

    return active_dict

def _find_in_pool(title, action_goals, amount_goals, time_goals):
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


def reset_progress(goal):
    if isinstance(goal, ActionGoal):
        goal.done = False
    elif isinstance(goal, AmountGoal):
        goal.current_amount = 0.0
    elif isinstance(goal, TimeGoal):
        goal.accumulated = timedelta()
    goal.status = GoalStatus.IN_PROGRESS


def load_goals_progress(active: dict, daily: dict, weekly: dict, custom: dict,
                          action_goals: list[ActionGoal], amount_goals: list[AmountGoal],
                          time_goals: list[TimeGoal]):
    daily_goals = []
    weekly_goals = []
    custom_goals = []

    for title, info in active.items():
        template = _find_in_pool(title, action_goals, amount_goals, time_goals)
        if template is None:
            continue

        goal = copy.deepcopy(template)  # isolate from the shared pool

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

    return daily_goals, weekly_goals, custom_goals



def get_initial_stats():
    stats = {}
    with open("config/initial.json", "r") as f:
        stats = json.load(f)
    return stats

def get_roles():
    roles = {}
    with open("config/roles.json", "r") as f:
        roles = json.load(f)
    return roles

def get_statuses():
    statuses = {}
    with open("config/statuses.json", "r") as f:
        statuses = json.load(f)
    return statuses

def get_available_skills():
    skills = []
    with open("config/skills.json", "r") as f:
        skills = json.load(f)
    return skills

def get_available_preferences():
    prefs = []
    with open("config/preferences.json", "r") as f:
        prefs = json.load(f)
    return prefs

def get_affinities(status, role, prefs, skills):

    global_prefs = get_available_preferences()
    global_skills = get_available_skills()
    global_statuses = get_statuses()
    global_roles = get_roles()

    affinity_prefs_creativity = 0
    affinity_prefs_intelligence = 0
    affinity_prefs_social = 0
    affinity_prefs_strength = 0
    affinity_prefs_mood = 0
    affinity_prefs_energy = 0
    affinity_prefs_stress = 0

    affinity_skills_creativity = 0
    affinity_skills_intelligence = 0
    affinity_skills_social = 0
    affinity_skills_strength = 0
    affinity_skills_mood = 0
    affinity_skills_energy = 0
    affinity_skills_stress = 0

    multiplier_roles_creativity = global_roles[role]["creativity"]
    multiplier_roles_intelligence = global_roles[role]["intelligence"]
    multiplier_roles_social = global_roles[role]["social"]
    multiplier_roles_strength = global_roles[role]["strength"]
    multiplier_roles_mood = global_roles[role]["mood"]
    multiplier_roles_energy = global_roles[role]["energy"]
    multiplier_roles_stress = global_roles[role]["stress"]

    multiplier_statuses_creativity = global_statuses[status]["creativity"]
    multiplier_statuses_intelligence = global_statuses[status]["intelligence"]
    multiplier_statuses_social = global_statuses[status]["social"]
    multiplier_statuses_strength = global_statuses[status]["strength"]
    multiplier_statuses_mood = global_statuses[status]["mood"]
    multiplier_statuses_energy = global_statuses[status]["energy"]
    multiplier_statuses_stress = global_statuses[status]["stress"]    

    for pref in prefs:
        affinity_prefs_creativity += global_prefs[pref]["affinity"]["creativity"]
        affinity_prefs_intelligence += global_prefs[pref]["affinity"]["intelligence"]
        affinity_prefs_social += global_prefs[pref]["affinity"]["social"]
        affinity_prefs_strength += global_prefs[pref]["affinity"]["strength"]
        affinity_prefs_mood += global_prefs[pref]["affinity"]["mood"]
        affinity_prefs_energy += global_prefs[pref]["affinity"]["energy"]
        affinity_prefs_stress += global_prefs[pref]["affinity"]["stress"]

    for skill in skills:
        affinity_skills_creativity += global_skills[skill]["affinity"]["creativity"]
        affinity_skills_intelligence += global_skills[skill]["affinity"]["intelligence"]
        affinity_skills_social += global_skills[skill]["affinity"]["social"]
        affinity_skills_strength += global_skills[skill]["affinity"]["strength"]
        affinity_skills_mood += global_skills[skill]["affinity"]["mood"]
        affinity_skills_energy += global_skills[skill]["affinity"]["energy"]
        affinity_skills_stress += global_skills[skill]["affinity"]["stress"]    

    return {
        "creativity": affinity_prefs_creativity,
        "intelligence": affinity_prefs_intelligence,
        "social": affinity_prefs_social,
        "strength": affinity_prefs_strength,
        "mood": affinity_prefs_mood,
        "energy": affinity_prefs_energy,
        "stress": affinity_prefs_stress
    }, {
        "creativity": affinity_skills_creativity,
        "intelligence": affinity_skills_intelligence,
        "social": affinity_skills_social,
        "strength": affinity_skills_strength,
        "mood": affinity_skills_mood,
        "energy": affinity_skills_energy,
        "stress": affinity_skills_stress
    }, {
        "creativity": multiplier_roles_creativity,
        "intelligence": multiplier_roles_intelligence,
        "social": multiplier_roles_social,
        "strength": multiplier_roles_strength,
        "mood": multiplier_roles_mood,
        "energy": multiplier_roles_energy,
        "stress": multiplier_roles_stress
    }, {
        "creativity": multiplier_statuses_creativity,
        "intelligence": multiplier_statuses_intelligence,
        "social": multiplier_statuses_social,
        "strength": multiplier_statuses_strength,
        "mood": multiplier_statuses_mood,
        "energy": multiplier_statuses_energy,
        "stress": multiplier_statuses_stress
    }







def save_dict(value):
    return json.dumps(value)

def get_dict(raw):
    default={}
    if raw:
        return json.loads(raw)
    return default

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



def check_registration(version):
    if version is None:
        return True
    version = Version(version)
    with open("config/register_fields.json", "r") as f:
        data = json.load(f)
    for ver in data.keys():
        if version < Version(ver):
            return True
    return False

def get_latest():
    return date(date.today().year-12, date.today().month, date.today().day)

def get_earliest():
    return date(date.today().year-100, date.today().month, date.today().day)

def to_seconds(time_str: str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def format_time_left_days(finish_time):
    delta = finish_time - datetime.now()
    if delta.total_seconds() <= 0:
        return "Time left: 0:00:00:00"

    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"Time left: {days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_time_left_hours(finish_time):
    delta = finish_time - datetime.now()
    if delta.total_seconds() <= 0:
        return "Time left: 0:00:00:00"

    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"Time left: {hours:02d}:{minutes:02d}:{seconds:02d}"

def parse_time_string(duration: str) -> timedelta:
    h, m, s = (int(x) for x in duration.split(":"))
    return timedelta(hours=h, minutes=m, seconds=s)

def add_time(current_time, max):
    t = datetime.strptime(current_time, "%H:%M:%S") + timedelta(seconds=10)
    maximum = datetime.strptime(max, "%H:%M:%S")
    if t > maximum:
        result = current_time
    else:
        result = t.strftime("%H:%M:%S")
    return result

def remove_time(current_time, min):
    t = datetime.strptime(current_time, "%H:%M:%S") - timedelta(seconds=10)
    minimum = datetime.strptime(min, "%H:%M:%S")
    if t < minimum:
        result = current_time
    else:
        result = t.strftime("%H:%M:%S")
    return result

def get_required_exp(level):
    with open("config/levels.json", "r") as f:
        levels = json.load(f)
    return levels[str(level)]