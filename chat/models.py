import datetime

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
    AbstractUser
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from .manager import UserManager, RoomManager
from django.db import IntegrityError
from channels.db import database_sync_to_async
class Room(models.Model):
    name = models.CharField(max_length=70)
    maximum_user = models.IntegerField(validators=[MaxValueValidator(15)], default=0)
    actual_logged_users = models.IntegerField(default=0)
    password = models.CharField(max_length=200)
    # objects = RoomManager()
    room_photo = models.ImageField(null=True, upload_to='images/')

    @classmethod
    def create_room(cls, *args, **kwargs):
        print("esa")
        similar_rooms = Room.objects.filter(name=kwargs['name']).exists()
        if similar_rooms:
            raise IntegrityError("You can't duplicate data in the database")
        print("wykonano")
        cls.objects.create(*args, **kwargs)

    async def add_user(self):
        if self.actual_logged_users < self.maximum_user:
            self.actual_logged_users += 1
        else:
            raise Exception("Your room users reached")
        await self.save_async()

    async def remove_user(self):
        if self.actual_logged_users > 0:
            self.actual_logged_users -= 1
        else:
            raise Exception("You can't remove user, cant minus from 0")
        await self.save_async()

    @database_sync_to_async
    def save_async(self, force_insert=False,
                  force_update=False, using=None, update_fields=None):
        return super().save(force_insert=False,
                  force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"Room {self.id}"

    def __repr__(self):
        return f"Room, name:{self.name} maximum_user:{self.maximum_user}" \
               f" actual_logged_users:{self.actual_logged_users}, password:{self.password}"


class UserApp(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=60)
    username = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    password = models.CharField(max_length=200)
    email_address = models.EmailField(unique=True)
    objects = UserManager()
    is_active = True
    is_superuser = False
    is_staff = False


    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        '''
        Returns: None
            This function had been changed on only self.id
            Previous it was {user self.id}
        '''
        return str(self.id)

class Message(models.Model):
    sender = models.ForeignKey(UserApp, null=False, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=False, on_delete=models.CASCADE)
    message_content = models.CharField(max_length=300)
    data_sended = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message {self.room} {self.sender}"

class RoomLogs(models.Model):
    user = models.ForeignKey(UserApp, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    data_joined = models.DateTimeField(default=datetime.datetime.now())
    data_left = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return f"Object of RoomUsers user_id:{self.user} room_id:{self.room}"

