from dataclasses import dataclass

import docker

from docker_manager import DockerManager

@dataclass
class ServerLimits:
    max_servers: int
    max_ram: int
    max_swap: int
    max_cpu: int
    max_storage: int

    def __json__(self):
        return {
            "max_servers": self.max_servers,
            "max_ram": self.max_ram,
            "max_swap": self.max_swap,
            "max_cpu": self.max_cpu,
            "max_storage": self.max_storage
        }

@dataclass
class Server():
    container_uuid: str = None
    name: str = None
    description: str = None
    owned_by: str = None
    server_config_id: int = None

    public_status: str = None

    image: str = None
    install_command: str = None
    startup_command: str = None
    enviroment_variables: dict = None

    server_limits: ServerLimits = None

    max_databases: int = None
    max_backups: int = None

    visable_host: str = "localhost"
    port: int = None

    container_id: str = None

    def __post__init__(self):
        if self.container_id is not None:
            self.load_from_docker(self.container_id)

    def load_from_docker(self):
        manager = DockerManager()

        if self.container_id is None:
            raise ValueError("Container ID is required to load from docker")

        try:
            container = manager.get_container(self.container_id)
        except docker.errors.NotFound:
            raise ValueError("Container not found")

        container.reload()

        self.container_uuid = container.name
        self.name = container.name
        self.description = container.labels.get('description', None)
        self.owned_by = container.labels.get('owned_by', None)
        self.server_config_id = container.labels.get('server_config_id', None)
        self.public_status = container.labels.get('public_status', None)
        self.image = container.attrs['Config']['Image']
        self.install_command = container.labels.get('install_command', None)
        self.startup_command = container.labels.get('startup_command', None)
        self.enviroment_variables = manager.get_env_variables(container)
        self.server_limits = ServerLimits(
            max_servers=container.labels.get('max_servers', None),
            max_ram=container.labels.get('max_ram', None),
            max_swap = container.labels.get('max_swap', None),
            max_cpu=container.labels.get('max_cpu', None),
            max_storage=container.labels.get('max_storage', None)
        )
        self.max_databases = container.labels.get('max_databases', None)
        self.max_backups = container.labels.get('max_backups', None)
        self.visable_host = container.labels.get('visable_host', None)
        self.port = container.ports[0]['PublicPort']
        self.container_id = container.id

    def save_to_docker(self):
        manager = DockerManager()

        labels = {
            "name": self.name,
            "description": self.description,
            "owned_by": self.owned_by,
            "server_config_id": self.server_config_id,
            "public_status": self.public_status,
            "install_command": self.install_command,
            "startup_command": self.startup_command,
            "max_servers": self.server_limits.max_servers,
            "max_ram": self.server_limits.max_ram,
            "max_swap": self.server_limits.max_swap,
            "max_cpu": self.server_limits.max_cpu,
            "max_storage": self.server_limits.max_storage,
            "max_databases": self.max_databases,
            "max_backups": self.max_backups,
            "visable_host": self.visable_host,
        }

        if self.container_id is None:
            ## create the server rather than updating
            manager.client.containers.create(
                image=self.image,
                command=self.startup_command,
                name=self.container_uuid,
                detach=True,
                labels=labels,
                environment=self.enviroment_variables,
                host_name=self.visable_host,
                auto_remove=False,
                cpu_shares=self.server_limits.max_cpu,
                mem_limit=self.server_limits.max_ram,
                memswap_limit=self.server_limits.max_ram + self.server_limits.max_swap,
                ## set volume where containers root directory is stored in a folder on the machine located at '/mnt/server/{container_uuid}'
                volumes={
                    f"/mnt/server/{self.container_uuid}": {
                        "bind": "/mnt/server",
                        "mode": "rw"
                    }
                },
                working_dir=f"/mnt/server/{self.container_uuid}",
            )

        container = manager.get_container(self.container_id)

        ## update labels
        container.labels.update(labels)
        ## update env variables
        manager.update_env_variables(container, self.enviroment_variables)

    def stream_terminal_logs(self):
        manager = DockerManager()

        container = manager.get_container(self.container_id)
        logs = container.logs(stream=True)

        return logs

    def execute_command(self, command):
        manager = DockerManager()

        container = manager.get_container(self.container_id)
        exec_id = container.exec_run(command, stdout=True, stderr=True, detach=True)

        return exec_id

    def delete(self):
        manager = DockerManager()

        container = manager.get_container(self.container_id)
        container.remove(v=True, link=True, force=True)

    def start(self):
        manager = DockerManager()

        self.container_id = manager.run_container(self.image, self.startup_command)

    def stop(self):
        manager = DockerManager()

        manager.stop_container(self.container_id)

    def change_state(self, state):
        manager = DockerManager()

        if state == "start":
            manager.change_container_state(self.container_id, "starting")
            self.start()
            manager.change_container_state(self.container_id, "running")
        elif state == "stop":
            manager.change_container_state(self.container_id, "stopping")
            self.stop()
            manager.change_container_state(self.container_id, "stopped")
        elif state == "pause":
            manager.change_container_state(self.container_id, "pausing")
            manager.pause_container(self.container_id)
            manager.change_container_state(self.container_id, "paused")
        elif state == "unpause":
            manager.change_container_state(self.container_id, "unpausing")
            manager.unpause_container(self.container_id)
            manager.change_container_state(self.container_id, "running")
        elif state == "restart":
            manager.change_container_state(self.container_id, "stopping")
            manager.restart_container(self.container_id)
            manager.change_container_state(self.container_id, "running")
        elif state == "kill":
            manager.change_container_state(self.container_id, "stopping")
            manager.stop_container(self.container_id, kill=True)
            manager.change_container_state(self.container_id, "stopped")
        else:
            raise ValueError("Invalid action")

    def __json__(self):
        return {
            "name": self.name,
            "description": self.description,
            "owned_by": self.owned_by,
            "server_config_id": self.server_config_id,
            "image": self.image,
            "install_command": self.install_command,
            "startup_command": self.startup_command,
            "enviroment_variables": self.enviroment_variables,
            "server_limits": self.server_limits.__json__(),
            "max_databases": self.max_databases,
            "max_backups": self.max_backups,
            "visable_host": self.visable_host,
            "port": self.port,
            "container_id": self.container_id
        }