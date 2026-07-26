from dataclasses import dataclass

@dataclass
class Achievement:
    message: str
    task: str
    number: int
    reference_task: str
    completed: bool = False