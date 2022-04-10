import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SocialNetWorkConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect')
        await self.accept()
        typeWebSocket = 'SocialNetwork'
        await self.channel_layer.group_add(typeWebSocket, self.channel_name)
        print(
            f"Social Network WebSocket connected with mailbox type {typeWebSocket}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']

        typeWebSocket = 'SocialNetwork'
        await self.channel_layer.group_send(
            typeWebSocket,
            {
                'type': 'return_message',
                "data": data,
            }
        )

    async def return_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'data': data,
        }))

    async def disconnect(self, close_code):
        typeWebSocket = 'SocialNetwork'
        await self.channel_layer.group_discard(typeWebSocket, self.channel_name)
        print(
            f"Social Network WebSocket disconnected with mailbox type {typeWebSocket}")
