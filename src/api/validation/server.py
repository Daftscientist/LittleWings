from dataclasses import dataclass
from core.server import ServerLimits

@dataclass
class GetServerParams:
    server_id: int

@dataclass
class ServerCreateParams:
    name: str
    description: str
    owned_by: str
    server_config_id: int
    image: str
    install_command: str
    startup_command: str
    enviroment_variables: dict

    server_limits: ServerLimits

    max_databases: int
    max_backups: int

    visable_host: str = "localhost"
    port: int

@dataclass
class ServerEditParams:
    server_id: int
    data: dict

@dataclass
class DeleteServerParams:
    server_id: int