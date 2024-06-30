import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from validation.server import ServerCreateParams, GetServerParams, ServerEditParams, DeleteServerParams
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
            container_uuid=uuid.uuid4(),
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
    
    @validate(
        json=ServerEditParams  
    )
    @protected_route()
    async def patch(self, request, data: ServerEditParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()

        for item in data.data:
            if item.lower() not in server.__dict__:
                continue
            setattr(server, item.lower(), data.data[item])

        return response.json(
            {"status": "success", "server_id": data.server_id},
        )

    @validate(
        json=DeleteServerParams
    )
    @protected_route()
    async def delete(self, request, data: DeleteServerParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()
        server.delete()
        return response.json(
            {"status": "success", "server_id": None},
        )