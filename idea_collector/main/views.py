from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms import modelform_factory
from .forms import ItemForm
from .models import Item, ItemAudio, ItemImage, ItemVideo, SiteSettings

SiteSettingsForm = modelform_factory(
    SiteSettings, fields=['title', 'primary_color', 'text_color']
)


def settings_view(request):
  # Fetch the single existing instance from the database
  settings_obj = SiteSettings.get_solo()

  if request.method == 'POST':
    form = SiteSettingsForm(request.POST, instance=settings_obj)
    if form.is_valid():
      form.save()
      messages.success(
          request, 'Settings saved successfully!'
      )
      return redirect('settings')
  else:
    form = SiteSettingsForm(instance=settings_obj)

  return render(
      request, 'main/settings.html', {'form': form}
  )


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