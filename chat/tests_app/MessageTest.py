from django.test import TestCase
from chat.models import Message, UserApp, Room
from django.core.exceptions import ValidationError
from django.db import IntegrityError
class MessageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = UserApp(
            nickname="testData1",
            username="testData1",
            surname="testData1",
            password="test1231dA",
            email_address="testData@testowy.com",
        )
        cls.room = Room.objects.create(
            name='test',
            maximum_user=15,
            actual_logged_users=0,
            password='test'
        )

        cls.message = Message.objects.create(
            sender=cls.sender,
            room=cls.room,
            message_content="Esa",
        )

    def test_create_message(self):
        '''
            Test raise error when we have unfilled fields sender, room
        '''
        message_data = {
            'message_content': 'contet',
        }
        message = Message.objects.create(**message_data)

        with self.assertRaises(IntegrityError):
            message.save()

    def test_save_message(self):
        with self.assertRaises(IntegrityError):
             message = self.message.save()

        self.assertIsInstance(message, Message)
        self.assertIsInstance(message.sender, self.sender)
        self.assertIsInstance(message.room, self.room)
        self.assertEqual(message.room , self.room)
        self.assertEqual(message.sender, self.sender)
