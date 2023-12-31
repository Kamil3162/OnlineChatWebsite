import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from . import models
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
import json
import time
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.db import IntegrityError
from django.contrib.auth import get_user

class WSConsumer(AsyncWebsocketConsumer):
    _user_cache = {}

    async def connect(self, *args, **kwargs):
        room_id = self.scope['url_route']['kwargs']['pk']
        self.room = await self.get_room_name(room_id)
        self.room_group_name = f'R{self.room.name}'
        await self.room.add_user()
        # Add the user to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("polaczenie z websocket")
        await self.accept()

    @database_sync_to_async
    def get_room_name(self, id):
        return models.Room.objects.get(pk=id)

    @database_sync_to_async
    def save_message(self, userid, roomid, message):
        try:
            user = cache.get(f'user_{userid}')

            if not user:
                user = models.UserApp.objects.get(pk=userid)
                cache.set(f'user_{userid}', user)
            # Create a new message object
            message_object = models.Message.objects.create(
                room=self.room,
                sender=user,
                message_content=message
            )

            room_logs = self.insert_Room_log(
                user=user,
                room=self.room
            )

            # Prepare the message data as JSON
            message_data = json.dumps({
                'action': 'message',
                'user': userid,
                'roomId': roomid,
                'message': message,
                'userName': user.username + " " + user.surname,
                'time': message_object.data_sended.isoformat()
                # assuming you meant 'date_sent' instead of 'data_sended'
            })

            return message_data

        except models.UserApp.DoesNotExist:
            # Handle the case where the user does not exist
            raise Exception("User does not exist")

        except models.Room.DoesNotExist:
            # Handle the case where the room does not exist
            raise Exception("Room does not exist")

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.room.remove_user()
        await self.close()

    async def receive(self, text_data):
        text_data1 = json.loads(text_data)
        user_id = text_data1['user_id']
        try:
            user = await self.get_user_information(user_id)
            user_data = user.username + " " + user.surname
        except models.UserApp.DoesNotExist:
            user_data = None
        room_id = text_data1['room_id']
        message = text_data1['message']
        print(user_id, room_id, message)
        message_body = json.loads(
            await self.save_message(user_id, room_id, message))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_body['message'],
                "userId": user_id,
                "sender_data": user_data
            }
        )
        print("wysłano wiadomosc naura")
        print("----------------------")

    async def chat_message(self, event):
        message = event['message']
        user_id = event['userId']
        sender_data = event['sender_data']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'userId': user_id,
            'sender_data': sender_data
        }))

    async def send_response(self, text_data=None):
        print("Wyslano wiadomosc do server ciesz sie", flush=True)
        response = json.dumps({"message": text_data})
        await self.send(response)

    @database_sync_to_async
    def get_user_information(self, userid: int):
        try:
            print(self.user_cache)
            return self.user_cache[userid]
        except KeyError:
            print("Key doesnt exist")
            user = models.UserApp.objects.get(pk=userid)
            self.user_cache[userid] = user
            return user

    def insert_Room_log(self, user: models.UserApp, room: models.RoomLogs):
        print("to jest insert ")
        try:
            room_log_obj = models.RoomLogs.objects.get(
                user=user,
                room=room
            )
            print("esa")
        except models.RoomLogs.DoesNotExist:
            room_log = models.RoomLogs.objects.create(
                user=user,
                room=room
            )
            print("Object created successfully.")
        else:
            print("Object already exist.")
    @property
    def user_cache(self):
        return self._user_cache
    @user_cache.setter
    def user_cache(self, roomlogs):
        print(self._user_cache)
        for roomlog in roomlogs:
            userid = roomlog.user_id
            try:
                self.user_cache[userid] = models.UserApp.objects.get(userid)
            except models.UserApp.DoesNotExist:
                raise Exception("Object does not exist")


'''
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        print("witamy jestes placzony z kanalem")
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))
'''
