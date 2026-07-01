import os
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
    