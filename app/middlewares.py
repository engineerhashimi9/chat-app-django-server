
from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed


@database_sync_to_async
def get_user_from_token(token):

    try:
        jwt_auth = JWTAuthentication()

        # Validate JWT access token
        validated_token = jwt_auth.get_validated_token(token)

        # Get authenticated Django user
        return jwt_auth.get_user(validated_token)

    except (InvalidToken, TokenError, AuthenticationFailed):
        return AnonymousUser()


class JWTAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        # Read WebSocket headers
        headers = dict(scope.get("headers", []))

        auth_header = headers.get(
            b"authorization", b""
        ).decode("utf-8")

        parts = auth_header.split()

        # Default user
        user = AnonymousUser()

        # Expected format: Bearer ACCESS_TOKEN
        if len(parts) == 2 and parts[0].lower() == "bearer":

            user = await get_user_from_token(parts[1])

        # Add authenticated user to scope
        scope = dict(scope)
        scope["user"] = user

        return await self.inner(scope, receive, send)
