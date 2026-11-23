from django.db import models
from accounts.models import User
# Create your models here.


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    is_group = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class UserRoom(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    def get_email(self):
        return self.user.email


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    def get_email(self):
        return self.user.email