
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

# Initialize Django first
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from app.routing import websocket_urlpatterns
from app.middlewares import JWTAuthMiddleware


application = ProtocolTypeRouter({

    # HTTP requests
    "http": django_asgi_app,

    # WebSocket connections
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),

})
