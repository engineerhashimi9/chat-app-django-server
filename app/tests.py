import json

from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User
from app.models import Room, UserRoom, Message, Contact
from config.asgi import application


class AppAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            name="Owner",
            last_name="User",
        )
        self.peer = User.objects.create_user(
            email="peer@example.com",
            password="StrongPass123!",
            name="Peer",
            last_name="User",
        )
        self.room = Room.objects.create(name="Test Room", is_group=False)
        UserRoom.objects.create(user=self.user, room=self.room)
        UserRoom.objects.create(user=self.peer, room=self.room)

        login = self.client.post(reverse("login"), {
            "email": "owner@example.com",
            "password": "StrongPass123!",
        }, format="json")
        self.access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_room_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(reverse("room-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_room_list_and_detail(self):
        list_response = self.client.get(reverse("room-list"))
        detail_response = self.client.get(
            reverse("room-detail", args=[self.room.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(room["name"] == "Test Room" for room in list_response.data))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_room_create_rejects_unknown_recipient(self):
        response = self.client.post(reverse("room-list"), {
            "name": "Unknown Room",
            "reciver_email": "missing@example.com",
            "is_group": False,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_room_create_reuses_existing_direct_room(self):
        response = self.client.post(reverse("room-list"), {
            "name": "Renamed In Existing Room",
            "reciver_email": "peer@example.com",
            "is_group": False,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Room")

    def test_room_update_and_delete(self):
        update = self.client.put(reverse("room-detail", args=[self.room.id]), {
            "name": "Updated Room",
            "reciver_email": "peer@example.com",
            "is_group": False,
        }, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)

        delete = self.client.delete(
            reverse("room-detail", args=[self.room.id]))
        self.assertIn(delete.status_code,
                      (status.HTTP_200_OK, status.HTTP_201_CREATED))

    def test_message_crud_and_room_history(self):
        create = self.client.post(reverse("message-list"), {
            "room": self.room.id,
            "content": "Hello from API test",
        }, format="json")
        self.assertEqual(create.status_code, status.HTTP_200_OK)
        message_id = create.data["id"]

        list_response = self.client.get(reverse("message-list"))
        detail_response = self.client.get(
            reverse("message-detail", args=[message_id]))
        history_response = self.client.get(
            reverse("room-messages", args=[self.room.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)

        update = self.client.put(reverse("message-detail", args=[message_id]), {
            "room": self.room.id,
            "content": "Updated message",
        }, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)

        delete = self.client.delete(
            reverse("message-detail", args=[message_id]))
        self.assertEqual(delete.status_code, status.HTTP_200_OK)

    def test_message_detail_rejects_message_outside_user_rooms(self):
        other_room = Room.objects.create(name="Other Room")
        other_message = Message.objects.create(
            user=self.peer,
            room=other_room,
            content="Private message",
        )

        response = self.client.get(
            reverse("message-detail", args=[other_message.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contact_crud(self):
        create = self.client.post(reverse("contact-list"), {
            "name": "Peer Contact",
            "email": "peer@example.com",
        }, format="json")
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        contact_id = create.data["id"]

        list_response = self.client.get(reverse("contact-list"))
        detail_response = self.client.get(
            reverse("contact-detail", args=[contact_id]))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        update = self.client.put(reverse("contact-detail", args=[contact_id]), {
            "name": "Updated Contact",
            "email": "peer@example.com",
        }, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)

        delete = self.client.delete(
            reverse("contact-detail", args=[contact_id]))
        self.assertEqual(delete.status_code, status.HTTP_200_OK)

    def test_contact_detail_rejects_another_users_contact(self):
        contact = Contact.objects.create(
            name="Peer-only contact",
            email="peer-only@example.com",
            user=self.peer,
        )

        response = self.client.get(
            reverse("contact-detail", args=[contact.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # WebSocket tests
    async def test_chat_consumer(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/",
            headers=[
                (b"authorization", f"Bearer {self.access}".encode()),
            ],
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            "message": "Hello, this is a test message!",
        })
        response = await communicator.receive_json_from(timeout=2)
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello, this is a test message!")

        await communicator.disconnect()


class ChatWebSocketTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ws-owner@example.com",
            password="StrongPass123!",
            name="WS",
            last_name="Owner",
        )
        self.room = Room.objects.create(name="WebSocket Room")
        UserRoom.objects.create(user=self.user, room=self.room)
        self.token = str(AccessToken.for_user(self.user))

    def communicator(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/",
        )
        communicator.scope["headers"] = [
            (b"authorization", f"Bearer {self.token}".encode()),
        ]
        return communicator

    async def test_authenticated_member_can_send_message(self):
        communicator = self.communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(json.dumps({"message": "Hello over WebSocket"}))
        event = await communicator.receive_json_from(timeout=2)

        self.assertEqual(event["type"], "message")
        self.assertEqual(event["room_id"], self.room.id)
        self.assertEqual(event["user_id"], self.user.id)
        self.assertEqual(event["message"], "Hello over WebSocket")

        await communicator.disconnect()

    async def test_invalid_json_returns_error(self):
        communicator = self.communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to("not-json")
        event = await communicator.receive_json_from(timeout=2)

        self.assertEqual(event, {"error": "Invalid JSON"})
        await communicator.disconnect()

    async def test_unauthenticated_connection_is_closed(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/",
        )
        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4401)
