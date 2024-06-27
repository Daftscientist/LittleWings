from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route

class ServerView(HTTPMethodView):
    path = '/api/server'

    @protected_route()
    async def get(self, request):
        return response.json({"message": "Hello, World!"})
    
    