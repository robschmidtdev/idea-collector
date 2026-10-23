import json

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import modelform_factory
from django.http import JsonResponse
from django.db import models
from .forms import ItemForm, TagForm
from .models import (
    Item,
    ItemAudio,
    ItemImage,
    ItemVideo,
    SiteSettings,
    Tag,
    UserFilterPreference,
)

EXTRA_FILTER_KEYS = ("color", "media")
SORT_ORDER_VALUES = {value for value, _ in UserFilterPreference.SORT_CHOICES}

SiteSettingsForm = modelform_factory(
    SiteSettings, fields=['title', 'primary_color']
)

def settings_view(request):
    settings_obj = SiteSettings.get_solo()
    
    tags = Tag.objects.all()

    settings_form = SiteSettingsForm(instance=settings_obj)
    tag_form = TagForm()

    if request.method == 'POST':
        if 'save_settings' in request.POST:
            settings_form = SiteSettingsForm(request.POST, instance=settings_obj)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'Settings saved successfully!')
                return redirect('settings')

        elif 'save_tag' in request.POST:
            tag_id = request.POST.get('tag_id')
            if tag_id:
                tag_instance = get_object_or_404(Tag, pk=tag_id)
                tag_form = TagForm(request.POST, instance=tag_instance)
            else:       
                tag_form = TagForm(request.POST)

            if tag_form.is_valid():
                tag_form.save()
                messages.success(request, 'Tag saved successfully!')
                return redirect('settings')

        elif 'delete_tag' in request.POST:
            tag_id = request.POST.get('tag_id')
            tag_instance = get_object_or_404(Tag, pk=tag_id)
            tag_instance.delete()
            messages.success(request, 'Tag deleted successfully!')
            return redirect('settings')

    context = {
        'form': settings_form,    
        'tag_form': tag_form,      
        'tags': tags,               
    }
    return render(request, 'main/settings.html', context)


def items(request):
    pinned_items = Item.objects.filter(pinned=True).prefetch_related(
        "tags", "images", "videos", "audios", "referenced_items", "created_by"
    ).order_by("pin_order", "name")
    unpinned_items = Item.objects.filter(pinned=False).prefetch_related(
        "tags", "images", "videos", "audios", "referenced_items", "created_by"
    ).order_by("name")

    visible_filters = []
    sort_order = "name_asc"
    if request.user.is_authenticated:
        preference = UserFilterPreference.objects.filter(user=request.user).first()
        if preference:
            visible_filters = [
                key for key in preference.visible_filters
                if key in EXTRA_FILTER_KEYS
            ]
            if preference.sort_order in SORT_ORDER_VALUES:
                sort_order = preference.sort_order

    return render(
        request,
        "main/items.html",
        {
            "active": "items",
            "pinned_items": pinned_items,
            "unpinned_items": unpinned_items,
            "tags": Tag.objects.all(),
            "color_choices": Item.COLOR_CHOICES,
            "sort_choices": UserFilterPreference.SORT_CHOICES,
            "visible_filters": visible_filters,
            "sort_order": sort_order,
            "filter_prefs_in_db": request.user.is_authenticated,
        },
    )


def filter_preferences(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False}, status=403)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False}, status=400)

    visible_filters = data.get("visible_filters", [])
    if not isinstance(visible_filters, list):
        return JsonResponse({"ok": False}, status=400)

    visible_filters = [
        key for key in visible_filters if key in EXTRA_FILTER_KEYS
    ]

    sort_order = data.get("sort_order", "name_asc")
    if sort_order not in SORT_ORDER_VALUES:
        sort_order = "name_asc"

    preference, _ = UserFilterPreference.objects.get_or_create(user=request.user)
    preference.visible_filters = visible_filters
    preference.sort_order = sort_order
    preference.save(update_fields=["visible_filters", "sort_order"])
    return JsonResponse({"ok": True})


def item_toggle_pin(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not item.pinned:
        max_order = Item.objects.filter(pinned=True).aggregate(
            models.Max("pin_order")
        )["pin_order__max"]
        item.pin_order = (max_order or 0) + 1
        item.pinned = True
    else:
        item.pinned = False
        item.pin_order = None
    item.save(update_fields=["pinned", "pin_order"])
    return JsonResponse({"pinned": item.pinned})


def item_reorder(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    order = request.POST.getlist("order")
    for index, pk in enumerate(order, start=1):
        Item.objects.filter(pk=pk, pinned=True).update(pin_order=index)
    return JsonResponse({"ok": True})


def item_detail(request, pk):
    item = get_object_or_404(
        Item.objects.prefetch_related("tags", "images", "videos", "audios", "referenced_items", "referenced_items__tags"),
        pk=pk,
    )
    context = {
        "active": "items",
        "item": item,
    }
    return render(request, "main/item_detail.html", context)


def _save_media(item, request):
    for f in request.FILES.getlist("images"):
        ItemImage.objects.create(item=item, image=f)
    for f in request.FILES.getlist("videos"):
        ItemVideo.objects.create(item=item, video=f)
    for f in request.FILES.getlist("audios"):
        ItemAudio.objects.create(item=item, audio=f)


def _delete_media(model, field, item, pks):
    for media in model.objects.filter(item=item, pk__in=pks):
        getattr(media, field).delete(save=False)
        media.delete()


def _delete_media_selection(item, request):
    _delete_media(ItemImage, "image", item, request.POST.getlist("delete_images"))
    _delete_media(ItemVideo, "video", item, request.POST.getlist("delete_videos"))
    _delete_media(ItemAudio, "audio", item, request.POST.getlist("delete_audios"))


def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if request.user.is_authenticated:
                item.created_by = request.user
            item.save()
            form.save_m2m()

            _save_media(item, request)

            return redirect("item_detail", pk=item.pk)
    else:
        form = ItemForm()

    return render(request, "main/item_form.html", {"form": form, "active": "items"})


def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            _delete_media_selection(item, request)
            _save_media(item, request)

            return redirect("item_detail", pk=item.pk)
    else:
        form = ItemForm(instance=item)

    return render(
        request,
        "main/item_form.html",
        {"form": form, "item": item, "active": "items"},
    )


def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method != "POST":
        return redirect("item_detail", pk=item.pk)

    for image in item.images.all():
        image.image.delete(save=False)
    for video in item.videos.all():
        video.video.delete(save=False)
    for audio in item.audios.all():
        audio.audio.delete(save=False)
    item.delete()

    return redirect("items")