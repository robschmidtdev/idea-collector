from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField


class SiteSettings(models.Model):
  title = models.CharField(
      max_length=100, default='Drum xx Factory', verbose_name='Site title'
  )
  primary_color = models.CharField(
      max_length=7, default='#0d6efd', verbose_name='Primary color (hex)'
  )  # e.g. Bootstrap blue
  text_color = models.CharField(
      max_length=7, default='#212529', verbose_name='Text color (hex)'
  )  # e.g. dark gray

  def save(self, *args, **kwargs):
    # Ensure there is only ever one settings entry (singleton pattern)
    self.pk = 1
    super().save(*args, **kwargs)

  @classmethod
  def get_solo(cls):
    # Fetch the settings or create them with default values if none exist
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
    color = models.CharField(max_length=7, default="#6c757d", blank=True) # e.g. Bootstrap gray or a hex code
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
    name = models.CharField(max_length=255)
    description = RichTextField(
        blank=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="items")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_items",
    )

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