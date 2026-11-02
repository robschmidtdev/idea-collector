import html

from django.db import migrations


def move_images_into_description(apps, schema_editor):
    Item = apps.get_model('main', 'Item')
    ItemImage = apps.get_model('main', 'ItemImage')

    for item_image in ItemImage.objects.select_related('item'):
        item = item_image.item
        try:
            url = item_image.image.url
        except ValueError:
            continue

        markup = (
            '<figure class="image">'
            f'<img src="{html.escape(url, quote=True)}" '
            f'alt="{html.escape(item.name, quote=True)}">'
            '</figure>'
        )
        description = (item.description or '') + markup
        Item.objects.filter(pk=item.pk).update(description=description)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_customfilter'),
    ]

    operations = [
        migrations.RunPython(
            move_images_into_description,
            migrations.RunPython.noop,
        ),
        migrations.DeleteModel(
            name='ItemImage',
        ),
    ]
