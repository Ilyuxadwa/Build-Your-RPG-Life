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

def parse_tasks(path="content/tasks/"):
    parsed = {}
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
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


def get_required_exp(level):
    with open("config/levels.json", "r") as f:
        levels = json.load(f)
    return levels[str(level)]