from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.utils.html import strip_tags
import html


class SiteSettings(models.Model):
    title = models.CharField(
        max_length=100, default='Drum xx Factory', verbose_name='Site title'
    )
    primary_color = models.CharField(
        max_length=7, default='#0d6efd', verbose_name='Primary color (hex)'
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Site settings'

    class Meta:
        verbose_name = 'Site setting'
        verbose_name_plural = 'Site settings'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(max_length=7, default="#6c757d", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Item(models.Model):
    COLOR_CHOICES = [
        ("primary", "Primary (Blue)"),
        ("secondary", "Secondary (Gray)"),
        ("success", "Success (Green)"),
        ("danger", "Danger (Red)"),
        ("warning", "Warning (Yellow)"),
        ("info", "Info (Light Blue)"),
        ("light", "Light (Very Light)"),
    ]

    name = models.CharField(max_length=255)
    description = RichTextField(
        blank=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="items")

    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default="info",
        blank=True
    )

    pinned = models.BooleanField(default=False)
    pin_order = models.IntegerField(null=True, blank=True)

    referenced_items = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="referenced_from",
        verbose_name="Referenced Items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_items",
    )

    def get_plain_description(self):
        plain_text = strip_tags(self.description)
        return html.unescape(plain_text).strip()

    class Meta:
        ordering = ["name"]
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="items/images/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Item Image"
        verbose_name_plural = "Item Images"

    def __str__(self):
        return f"Image - {self.item.name}"


class ItemVideo(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    video = models.FileField(upload_to="items/videos/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Item Video"
        verbose_name_plural = "Item Videos"

    def __str__(self):
        return f"Video - {self.item.name}"


class ItemAudio(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="audios",
    )
    audio = models.FileField(upload_to="items/audios/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Item Audio"
        verbose_name_plural = "Item Audios"

    def __str__(self):
        return f"Audio - {self.item.name}"