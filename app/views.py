from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import RoomSerializer, MessageSerializer, ContactSerializer
from rest_framework.response import Response
from .models import Room, UserRoom, Message, Contact
from django.shortcuts import get_object_or_404
from accounts.models import User
from rest_framework.pagination import PageNumberPagination



class MessagePagination(PageNumberPagination):

    page_size = 30

    page_size_query_param = "page_size"

    max_page_size = 100

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
            serializer = self.serializer_class(room, data=request.data, context={'request': request})
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


class MessageListApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request):
        rooms = Room.objects.filter(userroom__user=request.user)
        messages = Message.objects.filter(room__in=rooms)
        serilizer = self.serializer_class(messages, many=True)
        return Response(serilizer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=403)


class MessageDetailApiView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            message = Message.objects.filter(room__in=rooms).get(id=id)
        except Message.DoesNotExist:
            return Response({"detail": "the message for this user does not exist"}, status=403)
        else:
            serializer = self.serializer_class(message)
            return Response(serializer.data, status=200)

    def put(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            message = Message.objects.filter(room__in=rooms).get(id=id)
        except Message.DoesNotExist:
            return Response({"detail": "the message for this user does not exist"}, status=403)
        else:
            serializer = self.serializer_class(message, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=403)

    def delete(self, request, id):
        rooms = Room.objects.filter(userroom__user=request.user)
        try:
            message = Message.objects.filter(room__in=rooms).get(id=id)
        except Message.DoesNotExist:
            return Response({"detail": "the message for this user does not exist"}, status=403)
        else:
            message.delete()
            return Response({"detail": "object deleted"}, status=200)


class ContactListApiView(APIView):
    serializer_class = ContactSerializer
    # permission_classes=[IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = self.serializer_class(contacts, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=403)


class ContactDetailApiView(APIView):
    serializer_class = ContactSerializer
    # permission_classes=[IsAuthenticated]
    def get(self,request,id) :
        try :
            contact=Contact.objects.filter(user=request.user).get(id=id)
        except Contact.DoesNotExist :
            return Response({"detail":"the contact does not exist"},status=403)
        else :
            serializer=self.serializer_class(contact) 
            return Response(serializer.data,status=200)
    def put(self,request,id) :
        try :
            contact=Contact.objects.filter(user=request.user).get(id=id)
        except Contact.DoesNotExist :
            return Response({"detail":"the contact does not exist"},status=403)
        else :
            serializer=self.serializer_class(contact,data=request.data, context={'request': request}) 
            if serializer.is_valid() :
                return Response(serializer.data,status=200)
            else :
                return Response(serializer.errors,status=403)
    def delete(self,request,id) :
        try :
            contact=Contact.objects.filter(user=request.user).get(id=id)
        except Contact.DoesNotExist :
            return Response({"detail":"the contact does not exist"},status=403)
        else :
            contact.delete()
            return Response({"detail":"object has been deleted"},status=200)

class RoomMessagesApiView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):

        # 1. Verify that the user belongs to the room
        room = get_object_or_404(
            Room.objects.filter(userroom__user=request.user),
            id=room_id
        )

        # 2. Get messages of this room only
        messages = (
            Message.objects
            .filter(room=room)
            .select_related("user")
            .order_by("-created_time", "-id")
        )

        # 3. Paginate messages
        paginator = MessagePagination()

        page = paginator.paginate_queryset(
            messages,
            request,
            view=self
        )

        # 4. Serialize messages
        serializer = MessageHistorySerializer(
            page,
            many=True
        )

        # 5. Return paginated response
        return paginator.get_paginated_response(
            serializer.data
        )
