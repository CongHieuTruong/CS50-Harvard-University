import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ArchiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect')
        await self.accept()
        typeMail = 'archive'
        await self.channel_layer.group_add(typeMail, self.channel_name)
        print(f"Archive WebSocket connected with mailbox type {typeMail}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        archived = text_data_json['archived']

        
        typeMail = 'archive'
        await self.channel_layer.group_send(
            typeMail,
            {
                'type': 'return_message',
                "content": content,
                "archived": archived
            }
        )
    async def return_message(self, event):
        content = event['content']
        archived = event['archived']
        await self.send(text_data=json.dumps({
            'content': content,
            'archived': archived
        }))

    async def disconnect(self, close_code):
        typeMail = 'archive'
        await self.channel_layer.group_discard(typeMail, self.channel_name)
        print(f"Archive WebSocket disconnected with mailbox type {typeMail}")

class SendEmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect')
        await self.accept()
        typeMail = 'compose'
        await self.channel_layer.group_add(typeMail, self.channel_name)
        print(f"Compose WebSocket connected with mailbox type {typeMail}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        senderUser = text_data_json['senderUser']
        recipients = text_data_json['recipients']

        
        typeMail = 'compose'
        await self.channel_layer.group_send(
            typeMail,
            {
                'type': 'return_message',
                "content": content,
                "senderUser": senderUser,
                "recipients": recipients,

            }
        )
    async def return_message(self, event):
        content = event['content']
        senderUser = event['senderUser']
        recipients = event['recipients']
        await self.send(text_data=json.dumps({
            'content': content,
            'senderUser': senderUser,
            'recipients': recipients
        }))

    async def disconnect(self, close_code):
        typeMail = 'compose'
        await self.channel_layer.group_discard(typeMail, self.channel_name)
        print(f"Compose WebSocket disconnected with mailbox type {typeMail}")

class MakeReadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect')
        await self.accept()
        typeMail = 'read'
        await self.channel_layer.group_add(typeMail, self.channel_name)
        print(f"Read WebSocket connected with mailbox type {typeMail}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']

        
        typeMail = 'read'
        await self.channel_layer.group_send(
            typeMail,
            {
                'type': 'return_message',
                "content": content,
            }
        )
    async def return_message(self, event):
        content = event['content']
        await self.send(text_data=json.dumps({
            'content': content,
        }))

    async def disconnect(self, close_code):
        typeMail = 'read'
        await self.channel_layer.group_discard(typeMail, self.channel_name)
        print(f"Read WebSocket disconnected with mailbox type {typeMail}")