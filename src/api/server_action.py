import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from core.server import Server
from validation.server_action import ActionGetParams, ActionChangeParams

class ServerActionView(HTTPMethodView):
    path = '/api/server/action'

    @validate(
        json=ActionGetParams  
    )
    @protected_route()
    def get(self, request, data: ActionGetParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()
        return response.json({"current_status": server.public_status})

    @validate(
        json=ActionChangeParams  
    )
    @protected_route()
    def patch(self, request, data: ActionChangeParams):
        server = Server(
            container_id=data.server_id,
        )
        server.load_from_docker()

        server.change_state(data.action)

        return response.json({"status": "success", "server_id": data.server_id})