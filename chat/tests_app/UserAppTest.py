from django.test import TestCase
from chat.models import UserApp
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
class UserAppTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserApp(
            nickname="testData1",
            username="testData1",
            surname="testData1",
            password="test1231dA",
            email_address="testData@testowy.com",
        )
        cls.user_data = {
            "nickname": "testsave",
            "username": "testsave",
            "surname": "testsave",
            "password": "testsave",
            "email_address": "test@testsave.com",
        }

    def test_create_user(self):
        user = UserApp.objects.create_user(
            nickname="test1",
            username="test1",
            surname="test1",
            password="test1231",
            email_address="test@testowy.com",
        )
        self.assertIsInstance(user, UserApp)
        self.assertFalse(user.is_staff, "IsStaff should be false")
        self.assertFalse(user.is_superuser,
                        "IsSuperuser should be false")
        self.assertFalse(user.is_admin, "IsAdmin should be false")
    def test_create_superuser(self):
        nickname = "test1super"
        username = "test1super"
        surname = "test1super"
        password = "test1231super"
        email_address = "testsuper@testowy.com"
        superuser = UserApp.objects.create_superuser(
            nickname=nickname,
            username=username,
            surname=surname,
            password=password,
            email_address=email_address
        )
        self.assertEqual(superuser.nickname, nickname)
        self.assertTrue(check_password(password, superuser.password))
        self.assertTrue(superuser.is_staff, "IsStaff should be true")
        self.assertTrue(superuser.is_superuser, "IsSuperuser should be true")
        self.assertTrue(superuser.is_admin, "IsAdmin should be true")

    def test_create_moderator(self):pass

    def test_check_field_mandatory(self):
        user = UserApp()

        # Save the user without required fields
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()   # return all information about fields in model

        # Assert that specific error messages are present
        expected_error_messages = [
            'This field cannot be blank.',
            'This field cannot be blank.',
            'This field cannot be blank.',
            'This field cannot be blank.',
            'This field cannot be blank.',
        ]

        self.assertCountEqual(expected_error_messages,
                              cm.exception.messages)

        user.email_address = "testmail@dsa.pl"
        user.password = "3222"
        user.nickname = "test"
        user.surname = "test"
        user.username = "test"
        try:
            user.full_clean()
        except ValidationError:
            self.fail("Saving user with required fields raised a ValidationError")
        except ValueError:
            self.fail("Saving user with required fields raised a ValueError")

    def test_create_user_attributes(self):
        '''
            Test are perming on model creating on start of execution
            my global test in setUpDataTest
        '''
        user_data = {
            "nickname": "testData1",
            "username": "testData1",
            "surname": "testData1",
            "password": "test1231dA",
            "email_address": "testData@testowy.com",
        }
        self.assertEqual(self.user.nickname, user_data['nickname'])
        self.assertEqual(self.user.username, user_data.get('username'))
        self.assertEqual(self.user.surname, user_data.get('surname'))
        self.assertEqual(self.user.password, user_data.get('password'))
        self.assertEqual(self.user.email_address, user_data.get('email_address'))

    def test_create_user_database(self):
        user = UserApp.objects.create_user(**self.user_data)

        try:
            saved_user = UserApp.objects.get(pk=user.pk)
        except UserApp.DoesNotExist:
            self.fail("User was not saved in database")

    def test_proper_login(self):
        user = UserApp.objects.create_user(
            **self.user_data
        )
        response = self.client.post('/login', data={
            'email_address': user.email_address,
            'password': user.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_authenticated)


    def test_unique_email_field(self):
        # Create new user with our test data
        user1 = UserApp.objects.create_user(**self.user_data)
        try:
            user2 = UserApp.objects.create_user(**self.user_data)
        except IntegrityError:
            self.fail("Email address is a unique field")