import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from core.server import Server
from validation.manage import EditConfigValues

CONFIG_VALUES = [
    "DaemonName",
    "DaemonDescription",
    "DaemonHost",
    "DaemonHostAlias",
    "FrontendEggEndpoint"
]

class DaemonAuthView(HTTPMethodView):
    path = '/api/daemon/auth'

    @protected_route()
    async def get(self, request):
        app = request.app

        async with app.ctx.db_session() as session:
            async with session.begin():
                keys = await session.execute("SELECT * FROM auth_keys")
                keys = keys.fetchall()
                    
                keys = [{"key": item[0], "info": item[1]} for item in keys]

        return response.json({"status": "success", "data": keys})

    @protected_route()
    async def post(self, request):
        app = request.app

        new_key = await app.ctx.gen_key()

        return response.json({"status": "success", "key": new_key})

class DaemonManageView(HTTPMethodView):
    path = '/api/daemon/manage'

    @protected_route()
    async def get(self, request):
        app = request.app

        async with app.ctx.db_session() as session:
            async with session.begin():
                config = await session.execute("SELECT * FROM config")
                config = config.fetchall()

                config = {item[0]: item[1] for item in config}
                for item in config:
                    if item not in CONFIG_VALUES:
                        del config[item]

        return response.json({"status": "success", "data": config})

    @validate(
        json=EditConfigValues
    )
    @protected_route()
    async def patch(self, request, data: EditConfigValues):

        app = request.app

        for item in data.config_values:
            if item not in CONFIG_VALUES:
                return response.json({"status": "error", "error": "Invalid config value"})
        
        async with app.ctx.db_session() as session:
            async with session.begin():
                for key, value in data.config_values.items():
                    await session.execute(f"UPDATE config SET value = '{value}' WHERE key = '{key}'")

        return response.json({"status": "success"})