import os
import django
from django.core.management import call_command

django.setup()

from django.contrib.auth.models import User

admin_user = os.getenv("DJANGO_ADMIN_USER")

call_command('makemigrations')
call_command('migrate')

try:
    admin = User.objects.get(username=admin_user)
except User.DoesNotExist:
    call_command('createsuperuser', '--noinput', username=admin_user, email=os.getenv("DJANGO_ADMIN_EMAIL"))
    admin = User.objects.get(username=admin_user)
    admin.set_password(os.getenv("DJANGO_ADMIN_PASWWORD"))
    admin.save()
