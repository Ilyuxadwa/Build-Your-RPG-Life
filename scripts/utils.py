import json
import os
from packaging.version import Version
from datetime import datetime, date, timedelta
from flet import Icons
from goals import ActionGoal, AmountGoal, TimeGoal, InputMode

with open("config/icons.json", "r", encoding="utf-8") as f:
    icon_map = json.load(f)

def parse_tasks():
    parsed = {}
    groups = os.listdir("content/tasks/")
    for group in groups:
        files = os.listdir("content/tasks/"+group)
        parsed[group] = {}
    return parsed

def get_task():
    pass

def get_group():
    pass


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

def get_required_exp(level):
    with open("config/levels.json", "r") as f:
        levels = json.load(f)
    return levels[str(level)]