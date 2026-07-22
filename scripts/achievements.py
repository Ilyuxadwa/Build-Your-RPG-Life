from dataclasses import dataclass

@dataclass
class Achievement:
    identifier: str
    message: str
    task: str
    completed: bool
    number: int
    reference_task = "path/to/task"