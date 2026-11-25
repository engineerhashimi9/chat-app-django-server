import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from app.routing import websocket_urlpatterns

from app.middlewares import (
    JWTAuthMiddleware,
    OptionalOriginValidator
)


application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": OptionalOriginValidator(

        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),

        allowed_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    ),

})