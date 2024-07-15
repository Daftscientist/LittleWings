from dataclasses import dataclass

@dataclass
class FilesystemGetParams:
    server_id: int
    path: str = "/"