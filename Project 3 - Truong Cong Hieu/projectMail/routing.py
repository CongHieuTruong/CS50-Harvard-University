from unicodedata import name
from django.urls import path

from . import consumers

ws_urlpatterns = [
    path('ws/emails/archive', consumers.ArchiveConsumer.as_asgi(), name ='ws/emails/archive' ),
    path('ws/emails/compose', consumers.SendEmailConsumer.as_asgi(), name ='ws/emails/compose' ),
    path('ws/emails/read', consumers.MakeReadConsumer.as_asgi(), name ='ws/emails/read' ),
]