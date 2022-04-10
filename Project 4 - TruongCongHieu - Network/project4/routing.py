from unicodedata import name
from django.urls import path

from . import consumers

ws_urlpatterns = [
    path('ws/user/social-network', consumers.SocialNetWorkConsumer.as_asgi(),
         name='ws/user/social-network'),

]
