from django.urls import path
from . import views

urlpatterns = [
    # room api
    path("room", views.RoomListApiView.as_view(), name="room-list"),
    path("room/<int:id>", views.RoomDetailApiView.as_view(), name="room-detail"),
    # message api
    path("message",views.MessageListApiView.as_view(),name="message-list"),
    path("message/<int:id>",views.MessageListApiView.as_view(),name="message-list"),
    # contact api
]
