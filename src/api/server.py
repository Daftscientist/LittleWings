import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from validation.server import ServerCreateParams, GetServerParams
from core.server import Server

class ServerView(HTTPMethodView):
    path = '/api/server'

    @validate(
      json=GetServerParams  
    )
    @protected_route()
    async def get(self, request, data: GetServerParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()
        return response.json(server.__json__())
    
    @validate(
        json=ServerCreateParams  
    )
    @protected_route()
    async def post(self, request, data: ServerCreateParams):
        server = Server(
            container_uuid=uuid.uuid4()
            name=data.name,
            description=data.description,
            owned_by=request.headers['Authorization'],
            server_config_id=data.server_config_id,
            image=data.image,
            install_command=data.install_command,
            startup_command=data.startup_command,
            enviroment_variables=data.enviroment_variables,
            server_limits=data.server_limits,
            max_databases=data.max_databases,
            max_backups=data.max_backups,
            visable_host=data.visable_host,
            port=data.port,
        )
        server.save_to_docker()
        return response.json(
            {"status": "success", "server_id": server.container_uuid},
        )
    