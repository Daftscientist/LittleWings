from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate

class ServerView(HTTPMethodView):
    path = '/api/server'

    async def get(self, request):
        ...
    
    