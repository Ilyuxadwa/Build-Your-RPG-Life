import os
def parse_data():
    parsed = {}
    groups = os.listdir("tasks/")
    for group in groups:
        files = os.listdir("tasks/"+group)
        print(group)
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