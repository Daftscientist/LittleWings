import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from core.server import Server
from validation.server_filesystem import FilesystemGetParams

class FileSystem(HTTPMethodView):
    path = '/api/server/file_system'

    @validate(
        json=FilesystemGetParams  
    )
    @protected_route()
    async def get(self, request, data: FilesystemGetParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()
        
        files = server.get_dir_list(data.path)
        return response.json(
            {
                "files": files
            }
        )

    