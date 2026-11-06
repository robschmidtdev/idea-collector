import re

from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.views import serve as static_serve
from django.urls import include, path, re_path
from django.views.static import serve


def media_serve(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path(
        'favicon.ico',
        static_serve,
        {'path': 'main/favicon.ico', 'insecure': True},
    ),
]

media_url_pattern = settings.MEDIA_URL.lstrip('/')
urlpatterns += [
    re_path(rf"^{re.escape(media_url_pattern)}(?P<path>.*)$", media_serve),
]

static_url_pattern = settings.STATIC_URL.lstrip('/')
urlpatterns += [
    re_path(
        rf"^{re.escape(static_url_pattern)}(?P<path>.*)$",
        static_serve,
        {"insecure": True},
    ),
]
