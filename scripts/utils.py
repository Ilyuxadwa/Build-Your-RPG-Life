import json
import os
import random
from packaging.version import Version
from datetime import datetime, date, timedelta
from flet import Icons
from goals import ActionGoal, AmountGoal, TimeGoal, InputMode
from tasks import ActionTask, AmountTask, TimeTask

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
        return ActionTask(**common, stats=data["stats"])
    elif task_type == "amount":
        return AmountTask(
            **common,
            amount_input_mode=data["amount_input_mode"],
            min=data["min"],
            max=data["max"],
            amount_inputs_multipliers=data["amount_inputs_multipliers"],
        )
    elif task_type == "time":
        return TimeTask(
            **common,
            time_input=data["time_input"],
            min=data["min"],
            max=data["max"],
            amount_inputs_multipliers=data["amount_inputs_multipliers"],
        )
    else:
        raise ValueError(f"Unknown task type: {task_type}")

def get_node(path, tasks):
    node = tasks
    for part in path.split("/"):
        node = node[part]
    return node


def parse_tasks():
    parsed = {}
    for name in os.listdir("content/tasks/"):
        full_path = os.path.join("content/tasks/", name)
        if os.path.isdir(full_path):
            parsed[name] = parse_tasks(full_path)
        elif name.endswith(".json"):
            parsed[name[:-5]] = parse_task_file(full_path)
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


def save_goals_progress(daily: list, weekly: list, custom: list):
    pass

def load_goals_progress(daily: dict, weekly: dict, custom: dict):
    pass



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


def get_required_exp(level):
    with open("config/levels.json", "r") as f:
        levels = json.load(f)
    return levels[str(level)]