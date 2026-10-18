from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Safety check: only run in development mode (DEBUG = True)!
        if settings.DEBUG and not request.user.is_authenticated:
            # Fetch the first superuser (admin) from the database
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                # Automatically log the user into the session
                login(request, superuser)

        response = self.get_response(request)
        return response