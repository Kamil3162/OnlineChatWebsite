import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from . import models
import random
from channels.generic.websocket import (
    AsyncWebsocketConsumer
)
from channels.consumer import SyncConsumer, AsyncConsumer
import json
import time
from channels.db import database_sync_to_async

class WSConsumer(AsyncWebsocketConsumer):

    async def connect(self, *args, **kwargs):
        room_id = self.scope['url_route']['kwargs']['pk']
        self.room = await self.get_room(room_id)
        print(self.room)
        self.room_group_name = f'test'
        self.room.add_user()
        # Add the user to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("polaczenie z websocket")
        await self.accept()

    @database_sync_to_async
    def get_room(self, id):
        return models.Room.objects.get(pk=id)

    @database_sync_to_async
    def save_message(self, userid, roomid, message):
        try:
            user = models.UserApp.objects.get(pk=userid)

            # Add the user to the room (assuming this method exists in your Room model)
            self.room.add_user()

            # Create a new message object
            message_object = models.Message.objects.create(
                room=self.room,
                sender=user,
                message_content=message
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
        self.room.remove_user()
        await self.close()

    async def receive(self, text_data):
        print("dostałem wiadomosc")
        text_data1 = json.loads(text_data)
        user_id = text_data1['user_id']
        room_id = text_data1['room_id']
        message = text_data1['message']
        print(user_id, room_id, message)
        message_body = json.loads(await self.save_message(user_id, room_id, message))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_body['message']
            }
        )
        print("wysłano wiadomosc naura")

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))

    async def send_response(self, text_data=None):
        print("Wyslano wiadomosc do server ciesz sie", flush=True)
        response = json.dumps({"message":text_data})
        await self.send(response)


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
