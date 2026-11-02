import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CKEditor5Storage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "location", os.path.join(settings.MEDIA_ROOT, "content", "ckeditor")
        )
        kwargs.setdefault(
            "base_url", urljoin(settings.MEDIA_URL, "content/ckeditor/")
        )
        super().__init__(*args, **kwargs)
