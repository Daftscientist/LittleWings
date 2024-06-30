from dataclasses import dataclass

@dataclass
class EditConfigValues:
    server_id: int
    config_values: dict