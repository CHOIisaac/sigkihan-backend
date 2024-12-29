from django.urls import path
from .consumers import InvitationConsumer

websocket_urlpatterns = [
    path('ws/invitations/', InvitationConsumer.as_asgi()),
]