import sanic
from views import API_VIEWS
from api.websocket import WebsocketView
from core.database import init_db, close_db

# Create the Sanic app
app = sanic.Sanic()

# Add the websocket route
app.add_websocket_route(WebsocketView.entry(), WebsocketView.path)

# Initiate the database
app.register_listener(close_db, "after_server_stop")
app.register_listener(init_db, "before_server_start")

# Add the API routes
for view in API_VIEWS:
    app.add_route(view.as_view(), view.path)

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
