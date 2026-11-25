from django.urls import path
from . import views

urlpatterns = [
    # room api
    path("room", views.RoomListApiView.as_view(), name="room-list"),
    path("room/<int:id>", views.RoomDetailApiView.as_view(), name="room-detail"),
    # message api
    path("message",views.MessageListApiView.as_view(),name="message-list"),
    path("message/<int:id>",views.MessageDetailApiView.as_view(),name="message-detail"),
    path(
    "room/<int:room_id>/messages/",
    views.RoomMessagesApiView.as_view(),
    name="room-messages"
),
    # contact api
    path("contact", views.ContactListApiView.as_view(), name="contact-list"),
    path("contact/<int:id>", views.ContactDetailApiView.as_view(), name="contact-detail"),
]
