import sanic
from views import API_VIEWS
from api.websocket import WebsocketView
from core.database import init_db, close_db
from core.authentication import protected_route

# Create the Sanic app
app = sanic.Sanic()

# Initiate the database
app.register_listener(close_db, "after_server_stop")
app.register_listener(init_db, "before_server_start")

# Add the websocket route
@protected_route()
@app.websocket('/api/ws')
async def websocket_handler(request, ws):
    view = WebsocketView()
    await view.entry(request, ws)

# Add the API routes
for view in API_VIEWS:
    app.add_route(view.as_view(), view.path)

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
