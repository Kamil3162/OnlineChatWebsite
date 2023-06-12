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
from .manager import UserManager

class Room(models.Model):
    name = models.CharField(max_length=70)
    maximum_user = models.IntegerField(validators=[MaxValueValidator(15)],
                                       default=0)
    actual_logged_users = models.IntegerField(default=0)
    password = models.CharField(max_length=200)
    # room_image = models.ImageField(upload_to='media', null=True, blank=True)

    def add_user(self):
        try:
            if self.actual_logged_users < self.maximum_user:
                self.actual_logged_users += 1
            else:
                raise Exception("Your room users reached")
        except Exception as e:
            print(f"Error {str(e)}")

    def remove_user(self):
        try:
            if self.actual_logged_users > 0:
                self.actual_logged_users -= 1
            else:
                raise Exception("You can remove user")
        except Exception as e:
            print(f"Error {str(e)}")

    def __str__(self):
        return f"room{self.id}"


class UserApp(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=60)
    username = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    password = models.CharField(max_length=200)
    email_address = models.EmailField(unique=True)
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE)
    objects = UserManager()
    is_active = True
    is_superuser = False
    is_staff = False

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['password']

    def assign_user_to_room(self, room:Room):
        self.room = room
        room.add_user()

    def remove_user_from_room(self, room:Room):
        self.room = None
        room.remove_user()

    def __str__(self):
        return f"user {self.id}"

class Message(models.Model):
    sender = models.ForeignKey(UserApp, null=False, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=False, on_delete=models.CASCADE)
    message_content = models.CharField(max_length=300)
    data_sended = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message {self.room} {self.sender}"


