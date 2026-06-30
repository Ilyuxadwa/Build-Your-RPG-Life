import os

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
    