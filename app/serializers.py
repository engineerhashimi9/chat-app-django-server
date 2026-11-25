from rest_framework import serializers
from .models import Room, Message, UserRoom, Contact
from accounts.models import User
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist


class RoomSerializer(serializers.ModelSerializer):
    reciver_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Room
        fields = ["name", "reciver_email", "is_group"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        try:
            reciver = User.objects.get(email=validated_data["reciver_email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"reciver_email": "user with this email does not exist."})

        if user == reciver:
            raise serializers.ValidationError(
                {"reciver_email": "you cant create room with yours"})

        existing_room = Room.objects.filter(
            is_group=False,
            userroom__user=user
        ).filter(userroom__user=reciver).annotate(
            num_users=Count('userroom')
        ).filter(
            num_users=2
        ).first()

        if existing_room:
            return existing_room

        room = Room.objects.create(name=validated_data["name"])

        UserRoom.objects.bulk_create([
            UserRoom(user=user, room=room),
            UserRoom(user=reciver, room=room)
        ])

        return room


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="get_email", read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get("request")
        attrs["user"] = request.user.id
        return super().validate(attrs)


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="get_email", read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get("request")
        attrs["user"] = request.user.id
        return super().validate(attrs)
class MessageHistorySerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = Message

        fields = [
            "id",
            "room",
            "user_email",
            "content",
            "created_time"
        ]