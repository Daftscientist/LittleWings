import uuid
from sanic.views import HTTPMethodView
from sanic import response
from sanic_ext import validate
from core.authentication import protected_route
## import validation
from core.server import Server
from validation.manage import EditConfigValues, DeleteAuthKeyParams
from views import CONFIG_VALUES
from sqlalchemy.future import select
from sqlalchemy import delete, update
from core.database import AuthKeys, Config

class DaemonAuthView(HTTPMethodView):
    path = '/api/daemon/auth'

    @protected_route()
    async def get(self, request):
        app = request.app

        async with app.ctx.db_session() as session:
            async with session.begin():
                # Assuming AuthKey is the ORM model representing the auth_keys table
                # and it has columns 'key' and 'info'
                result = await session.execute(select(AuthKeys))
                keys = result.scalars().all()

                keys = [{"key": item.key, "info": item.info} for item in keys]

        return response.json({"status": "success", "data": keys})

    @protected_route()
    async def post(self, request):
        app = request.app

        new_key = await app.ctx.gen_key()

        return response.json({"status": "success", "key": new_key})

    @validate(DeleteAuthKeyParams)
    @protected_route()
    async def delete(self, request, data: DeleteAuthKeyParams):
        app = request.app

        async with app.ctx.db_session() as session:
            async with session.begin():
                # Assuming AuthKey is the ORM model representing the auth_keys table
                # and it has a column 'key' that matches 'data.key'
                stmt = delete(AuthKeys).where(AuthKeys.key == data.key)
                await session.execute(stmt)

        return response.json({"status": "success"})

class DaemonManageView(HTTPMethodView):
    path = '/api/daemon/manage'

    @protected_route()
    async def get(self, request):
        app = request.app

        async with app.ctx.db_session() as session:
            async with session.begin():
                # Assuming Config is the ORM model representing the config table
                # and it has columns 'key' and 'value'
                result = await session.execute(select(Config))
                config_items = result.scalars().all()

                # Convert to dictionary and filter based on CONFIG_VALUES
                config = {item.key: item.value for item in config_items if item.key in CONFIG_VALUES}

        return response.json({"status": "success", "data": config})

    @validate(json=EditConfigValues)
    @protected_route()
    async def patch(self, request, data: EditConfigValues):
        app = request.app

        # Validate config values
        for item in data.config_values:
            if item not in CONFIG_VALUES:
                return response.json({"status": "error", "error": "Invalid config value"})

        async with app.ctx.db_session() as session:
            async with session.begin():
                # Assuming Config is the ORM model representing the config table
                # and it has columns 'key' and 'value'
                for key, value in data.config_values.items():
                    # Find the config item by key and update its value
                    stmt = (
                        update(Config)
                        .where(Config.key == key)
                        .values(value=value)
                    )
                    await session.execute(stmt)

        return response.json({"status": "success"})