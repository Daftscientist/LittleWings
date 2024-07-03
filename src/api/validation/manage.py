from dataclasses import dataclass

@dataclass
class EditConfigValues:
    config_values: dict

@dataclass
class DeleteAuthKeyParams:
    key: str