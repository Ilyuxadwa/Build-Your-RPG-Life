import json
import os
from packaging.version import Version
from datetime import datetime, date

def parse_tasks():
    parsed = {}
    groups = os.listdir("actions/tasks/")
    for group in groups:
        files = os.listdir("actions/tasks/"+group)
        for thing in files:
            if thing.endswith(".json"):
                get_task(thing)
            elif not thing.contains("."):
                get_group()
    return parsed

def get_task():
    pass

def get_group():
    pass



def get_latest():
    return date(date.today().year-12, date.today().month, date.today().day)

def get_earliest():
    return date(date.today().year-100, date.today().month, date.today().day)



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
    with open("config/register_fields.json", "r") as f:
        data = json.load(f)
    for ver in data.keys():
        if version < Version(ver):
            return True
    return False