from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import modelform_factory
from django.http import JsonResponse
from django.db import models
from .forms import ItemForm, TagForm
from .models import Item, ItemAudio, ItemImage, ItemVideo, SiteSettings, Tag

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
        "tags", "images", "videos", "audios", "created_by"
    ).order_by("pin_order", "name")
    unpinned_items = Item.objects.filter(pinned=False).prefetch_related(
        "tags", "images", "videos", "audios", "created_by"
    ).order_by("name")
    return render(
        request,
        "main/items.html",
        {
            "active": "items",
            "pinned_items": pinned_items,
            "unpinned_items": unpinned_items,
            "tags": Tag.objects.all(),
        },
    )


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
    item = get_object_or_404(Item, pk=pk)
    context = {
        "active": "items",
        "item": item,
    }
    return render(request, "main/item_detail.html", context)


def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if request.user.is_authenticated:
                item.created_by = request.user
            item.save()

            for f in request.FILES.getlist("images"):
                ItemImage.objects.create(item=item, image=f)
            for f in request.FILES.getlist("videos"):
                ItemVideo.objects.create(item=item, video=f)
            for f in request.FILES.getlist("audios"):
                ItemAudio.objects.create(item=item, audio=f)

            return redirect("item_detail", pk=item.pk)
    else:
        form = ItemForm()

    return render(request, "main/item_form.html", {"form": form, "active": "items"})