import json
from channels.generic.websocket import AsyncWebsocketConsumer


connected_users = {}


class InvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        print(self.channel_name)
            # 사용자 연결 저장
        connected_users[self.user.email] = self.channel_name
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 사용자 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 초대 메시지 수신
    async def send_invitation(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'invitation',
            'message': message
        }))