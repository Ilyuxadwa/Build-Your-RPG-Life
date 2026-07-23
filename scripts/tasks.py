from dataclasses import dataclass

@dataclass
class Task:
    title: str
    description: str
    cooldown_type: str
    cooldown: str
    available_for: list[str]
    recommended_for: list[str]
    additional_options_type: str
    additional_options_select: str
    additional_options: dict

@dataclass
class ActionTask(Task):
    stats: dict

@dataclass
class AmountTask(Task):
    amount_input_mode: str
    min: int
    max: int
    amount_inputs_multipliers: dict

@dataclass
class TimeTask(Task):
    time_input: str
    min: str
    max: str
    amount_inputs_multipliers: dict