# Generated manually for ItemFile

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_sitesettings_primary_color_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='items/files/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='main.item')),
            ],
            options={
                'verbose_name': 'Item File',
                'verbose_name_plural': 'Item Files',
                'ordering': ['created_at'],
            },
        ),
    ]
