from django.test import TestCase
from chat.models import UserApp


class UserAppTestCase(TestCase):
    def setUp(self) -> None:pass

    def test_creating_user(self):
        user = UserApp.objects.create_user(
            nickname="test1",
            username="test1",
            surname="test1",
            password="test1231",
            email_address="test@testowy.com",
        )
        print(user.password)
        self.assertIsInstance(user, UserApp)



    def test_create_user_attributes(self):pass

    def test_create_user_database(self):pass

