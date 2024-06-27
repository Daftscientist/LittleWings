import docker
import json

def get_env_variables(container):
    # Assuming `container` is a properly initialized container object
    env_vars_dict = {item.split('=')[0]: item.split('=')[1] for item in container.attrs['Config']['Env']}
    variables_label = container.labels.get('variables', '{}')

    variables = json.loads(variables_label)
    result = {var['name']: env_vars_dict.get(var['env_variable']) for var in variables if 'name' in var and 'env_variable' in var}

    return result

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def run_container(self, image, command):
        container = self.client.containers.run(image, command, detach=True)
        return container.id

    def stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()

    def list_containers(self):
        return self.client.containers.list()