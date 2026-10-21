from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import modelform_factory
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
    item_list = Item.objects.all()
    return render(
        request, "main/items.html", {"active": "items", "items": item_list}
    )


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