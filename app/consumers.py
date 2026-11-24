
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message, UserRoom


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        # 1. Get authenticated user
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        # 2. Get room ID from URL
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # 3. Check room membership
        if not await self.is_room_member():
            await self.close(code=4403)
            return

        # 4. Create a unique group for this room
        self.room_group_name = f"chat_{self.room_id}"

        # 5. Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 6. Accept WebSocket connection
        await self.accept()

        print(
            f"Connected: {self.user.email} "
            f"to room {self.room_id}"
        )

    async def disconnect(self, close_code):

        # Remove connection from room group
        if hasattr(self, "room_group_name"):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        print("WebSocket disconnected")

    async def receive(self, text_data):

        # 1. Parse incoming JSON
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            await self.send_json({
                "error": "Invalid JSON"
            })
            return

        if not isinstance(data, dict):
            await self.send_json({
                "error": "Invalid message format"
            })
            return

        # 2. Get message content
        message = data.get("message")

        if not isinstance(message, str):
            await self.send_json({
                "error": "Message must be a string"
            })
            return

        message = message.strip()

        if not message or len(message) > 2000:
            await self.send_json({
                "error": "Message must contain 1 to 2000 characters"
            })
            return

        # 3. Save message in database
        message_data = await self.save_message(message)

        if message_data is None:
            await self.send_json({
                "error": "You are not a member of this room"
            })
            return

        # 4. Send message to room members
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "data": message_data
            }
        )

    async def chat_message(self, event):

        # Send message to connected Flutter clients
        await self.send(
            text_data=json.dumps(event["data"])
        )

    @database_sync_to_async
    def is_room_member(self):

        return UserRoom.objects.filter(
            user_id=self.user.pk,
            room_id=self.room_id
        ).exists()

    @database_sync_to_async
    def save_message(self, content):

        # Check membership again before saving
        is_member = UserRoom.objects.filter(
            user_id=self.user.pk,
            room_id=self.room_id
        ).exists()

        if not is_member:
            return None

        # Save message
        message = Message.objects.create(
            user_id=self.user.pk,
            room_id=self.room_id,
            content=content
        )

        return {
            "type": "message",
            "id": message.id,
            "room_id": message.room_id,
            "user_id": message.user_id,
            "user": message.user.email,
            "user_name": (
                f"{message.user.name} {message.user.last_name}"
            ).strip(),
            "message": message.content,
            "created_time": message.created_time.isoformat()
        }
