import os
import docker
import json

import docker.models
import docker.models.containers

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def run_container(self, image, command):
        container = self.client.containers.run(image, command, detach=True)
        return container.id

    def stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()

    def list_dir(self, container_uuid, dir_path="/"):
        ## get files using the symlink path:
        """
           /mnt/server/{self.container_uuid} -local mount
        """

        ## get files using the symlink path:
        ## handle if dir not found


        files = os.listdir(f"/mnt/server/{container_uuid}{dir_path}")

        if not files:
            return []
        ## just fetch the names of files and directories

        return files
    
    def get_file(self, container_uuid, file_path):
        with open(f"/mnt/server/{container_uuid}{file_path}", "rb") as file:
            return file.read()

    def list_containers(self):
        return self.client.containers.list()

    def change_container_state(self, container_id, state):
        container = self.client.containers.get(container_id)
        container.labels.update({"public_status": state})

    def get_container(self, container_id) -> docker.models.containers.Container:
        return self.client.containers.get(container_id)
    
    def pause_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.pause()

    def stop_container(self, container_id, kill=False):
        container = self.client.containers.get(container_id)
        if kill:
            container.kill()
        else:
            container.stop()
    
    def unpause_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.unpause()
    
    def restart_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.restart()
    
    def get_container_logs(self, container_id):
        container = self.client.containers.get(container_id)
        return container.logs()
    
    def get_container_stats(self, container_id):
        container = self.client.containers.get(container_id)
        return container.stats(stream=False)

    def get_env_variables(self, container):
        # Assuming `container` is a properly initialized container object
        env_vars_dict = {item.split('=')[0]: item.split('=')[1] for item in container.attrs['Config']['Env']}
        variables_label = container.labels.get('variables', '{}')

        variables = json.loads(variables_label)
        result = {var['name']: env_vars_dict.get(var['env_variable']) for var in variables if 'name' in var and 'env_variable' in var}

        return result
    
    def update_env_variables(self, container, variables):
        container.labels['variables'] = json.dumps(variables)
        container.reload()
        env_vars = [f"{key}={value}" for key, value in variables.items()]
        container.update({'Env': env_vars})
        container.reload()