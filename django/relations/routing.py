from django.urls import re_path

from user import consumers

urlpatterns = [
    re_path(r"ws/status/", consumers.statusConsumer.as_asgi()),
]
