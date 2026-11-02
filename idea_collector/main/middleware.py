from django.contrib.auth.middleware import LoginRequiredMiddleware
from django.contrib.auth.models import User


class LoginRequiredWhenAccountExistsMiddleware(LoginRequiredMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not User.objects.exists():
            return None
        return super().process_view(request, view_func, view_args, view_kwargs)
