"""
ASGI config for smt project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import uvicorn

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smt.settings')

application = get_asgi_application()

if __name__ == "__main__":
    uvicorn.run("smt.asgi:application", host="0.0.0.0", port=8000, log_level="info")
