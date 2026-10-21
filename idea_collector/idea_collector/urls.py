from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from ckeditor_uploader import views as ckeditor_views

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    path(
        "ckeditor/upload/",
        ckeditor_views.upload,
        name="ckeditor_upload",
    ),
    path(
        "ckeditor/browse/",
        ckeditor_views.browse,
        name="ckeditor_browse",
    ),
]