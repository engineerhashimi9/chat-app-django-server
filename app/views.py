from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import RoomSerializer, MessageSerializer
from rest_framework.response import Response
from .models import Room, UserRoom, Message
from django.shortcuts import get_object_or_404
from accounts.models import User


class RoomListApiView(APIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(userroom__user=request.user)
        serializer = self.serializer_class(rooms, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=403)


class RoomDetailApiView(APIView):
    serializer_class = RoomSerializer

    def get(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            room = rooms.get(id=id)
        except Room.DoesNotExist:
            return Response({"detail": "room object does not exist"}, status=404)
        else:
            serializer = self.serializer_class(room)
            return Response(serializer.data, status=200)

    def put(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            room = rooms.get(id=id)
        except Room.DoesNotExist:
            return Response({"detail": "room object does not exist"}, status=404)
        else:
            serializer = self.serializer_class(room, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=403)

    def delete(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            room = rooms.get(id=id)
        except Room.DoesNotExist:
            return Response({"detail": "room object does not exist"}, status=404)
        else:
            room.delete()
            return Response({"detail": "object deleted!"}, status=201)


class MessageApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request):
        rooms = Room.objects.filter(userroom__user=request.user)
        messages = Message.objects.filter(room__in=rooms)
        serilizer = self.serializer_class(messages, many=True)
        return Response(serilizer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=403)
