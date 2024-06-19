from channels.routing import ProtocolTypeRouter,URLRouter
import os
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buptAirSys.settings")
django_asgi_app = get_asgi_application()


