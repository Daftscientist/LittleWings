from api.server import ServerView
from api.server_action import ServerActionView
from api.manage import DaemonManageView, DaemonAuthView

API_VIEWS = [
    ServerView,
    ServerActionView,
    DaemonManageView,
    DaemonAuthView
]