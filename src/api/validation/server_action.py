from dataclasses import dataclass

@dataclass
class ActionGetParams:
    server_id: int

@dataclass
class ActionChangeParams:
    server_id: int
    action: str
