from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Item,
    ItemAudio,
    ItemImage,
    ItemVideo,
    SiteSettings,
    Tag,
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1

    readonly_fields = ("image_preview",)
    fields = ("image", "image_preview")

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj.image:
            return "-"

        return format_html(
            '<img src="{}" style="max-height:150px; max-width:250px;" />',
            obj.image.url,
        )


class ItemVideoInline(admin.TabularInline):
    model = ItemVideo
    extra = 1

    readonly_fields = ("video_preview",)
    fields = ("video", "video_preview")

    @admin.display(description="Preview")
    def video_preview(self, obj):
        if not obj.video:
            return "-"

        return format_html(
            """
            <video width="250" controls>
                <source src="{}">
                Your browser does not support the video element.
            </video>
            """,
            obj.video.url,
        )


class ItemAudioInline(admin.TabularInline):
    model = ItemAudio
    extra = 1

    readonly_fields = ("audio_preview",)
    fields = ("audio", "audio_preview")

    @admin.display(description="Preview")
    def audio_preview(self, obj):
        if not obj.audio:
            return "-"

        return format_html(
            """
            <audio controls preload="none" style="width: 250px;">
                <source src="{}">
                Your browser does not support the audio element.
            </audio>
            """,
            obj.audio.url,
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [
        ItemImageInline,
        ItemVideoInline,
        ItemAudioInline,
    ]

    list_display = (
        "name",
        "color",
        "pinned",
        "pin_order",
        "created_by",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "color",
    )

    search_fields = (
        "name",
    )

    autocomplete_fields = (
        "created_by",
    )
    
    filter_horizontal = (
        "tags",
        "referenced_items",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "color",
                    "tags",
                    "referenced_items",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )