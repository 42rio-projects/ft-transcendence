from django.urls import re_path

from relations import consumers

urlpatterns = [
    re_path(r"ws/status/", consumers.statusConsumer.as_asgi()),
]
