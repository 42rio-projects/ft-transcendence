import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ft_transcendence.settings')

# Garanta que as configurações do Django sejam carregadas antes de acessar modelos ou rotas
django_asgi_app = get_asgi_application()

def get_application():
    import django
    django.setup()  # Carrega as configurações do Django

    # Importe suas rotas somente depois que as configurações do Django estiverem carregadas
    from chat.routing import websocket_urlpatterns
    from pong.routing import websocket_urlpatterns
    from relations.routing import websocket_urlpatterns

    return ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })

application = get_application()
