from django.urls import path
from . import views

urlpatterns = [
    path("room", views.RoomListApiView.as_view(), name="room-list"),
    path("room/<int:id>", views.RoomDetailApiView.as_view(), name="room-detail"),
    path("message",views.MessageApiView.as_view(),name="message-list")
]
