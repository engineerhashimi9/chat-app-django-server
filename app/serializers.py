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

        user_room_ids = UserRoom.objects.filter(
            user=user).values_list("room_id", flat=True)
        existing_room = (
            Room.objects.filter(
                id__in=user_room_ids,
                is_group=False,
                userroom__user=reciver,
            )
            .distinct()
            .first()
        )

        if existing_room:
            return existing_room

        room = Room.objects.create(
            name=validated_data["name"],
            is_group=validated_data.get("is_group", False),
        )

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
    def validate_content(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        if len(value) > 2000:
            raise serializers.ValidationError(
                "Message cannot exceed 2000 characters."
            )

        return value


    def validate(self, attrs):

        request = self.context.get("request")

        room = attrs.get("room")

        if room is None:
            raise serializers.ValidationError(
                {"room": "Room is required."}
            )

        is_member = UserRoom.objects.filter(
            user=request.user,
            room=room
        ).exists()

        if not is_member:
            raise serializers.ValidationError({
                "room": "You are not a member of this room."
            })

        # Always use authenticated user
        attrs["user"] = request.user

        return attrs


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="get_email", read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get("request")
        attrs["user"] = request.user
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
