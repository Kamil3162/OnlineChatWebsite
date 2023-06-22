from django.contrib.auth.models import BaseUserManager
from django.db import models, IntegrityError
class UserManager(BaseUserManager):

    def create_user(self, nickname, username, surname, password, email_address):
        if not nickname:
            raise ValueError("Nickname is empty")
        if not username:
            raise ValueError("Username is empty")
        if not surname:
            raise ValueError("Surname is empty")
        email_address = self.normalize_email(email_address)
        user = self.model(
            nickname=nickname,
            username=username,
            surname=surname,
            email_address=email_address
        )
        user.set_password(password)
        user.save()
        return user

    def create_moderator(self, nickname, username, surname, password, email_address):
        user = self.create_user(nickname, username, surname, password, email_address)
        user.is_staff = True
        user.is_admin = True
        return user

    def create_superuser(self, nickname, username, surname, password, email_address):
        user = self.create_user(nickname, username, surname, password, email_address)
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        return user

    def change_user_permissions(self, User, permisions):
        pass

class RoomManager(models.Manager):
    def create(self, *args, **kwargs):
        super(RoomManager, self).create(*args, **kwargs)

