from django.contrib import admin
from .models import Room, UserRoom, Contact, Message
# Register your models here.
admin.site.register(Room)
admin.site.register(UserRoom)
admin.site.register(Contact)
admin.site.register(Message)
