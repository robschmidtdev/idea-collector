from django.contrib.auth.models import User

from .models import SiteSettings


def site_settings(request):
  return {'settings': SiteSettings.get_solo()}


def account_status(request):
  return {'can_register': not User.objects.exists()}
