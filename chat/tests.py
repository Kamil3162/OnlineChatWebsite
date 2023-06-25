import random
import string
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.hashers import make_password, check_password
from .models import Room


class RoomTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(
            name='test',
            maximum_user=15,
            actual_logged_users=0,
            password="test"
        )
        print(cls.room.password)
    def test_password_hashing(self):
        letters = string.ascii_letters
        random_selector = random.Random()
        letter_generator = random_selector.choice

        self.assertTrue(check_password('123456', self.room.password),
                        msg="The password hashing test failed. The passwords do not match.")

        for _ in range(15):
            rand_password = ''.join([letter_generator(letters) for _ in range(30)])
            self.assertFalse(check_password(rand_password, self.room.password),
                             msg="You entered a bad password. Please change it.")

    def test_exceed_max_user(self):
        self.room.actual_logged_users = self.room.maximum_user

        with self.assertRaises(Exception) as context:
            self.room.add_user()

        self.assertEqual(str(context.exception), "Your room users reached")

    def test_add_users(self):
        initial_users = self.room.actual_logged_users
        self.room.add_user()
        self.assertEqual(self.room.actual_logged_users, initial_users, msg="Instance method doesn't work properly")

    def test_minus_users(self):
        initial_users = self.room.actual_logged_users
        self.room.remove_user()
        self.assertEqual(self.room.actual_logged_users, initial_users, msg="Method doesn't work properly")

    def test_string_object_representation(self):
        self.assertEqual(f"Room {self.room.id}", str(self.room))

    def test_repr_object_representation(self):
        expected_repr = (
            f"Room, "
            f"name:{self.room.name} "
            f"maximum_user:{self.room.maximum_user} "
            f"actual_logged_users:{self.room.actual_logged_users} "
            f"password:{self.room.password}"
        )

        actual_repr = repr(self.room)

        self.assertEqual(expected_repr, actual_repr, "The __repr__ method should return the expected string representation.")

    def test_create_same_rooms(self):
        room_data = {
            'name': 'test',
            'maximum_user': 15,
            'actual_logged_users': 0,
            'password': 'test'
        }

        with self.assertRaises(IntegrityError):
            room = Room.create_room(**room_data)

