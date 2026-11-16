import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomFilter, Item, Tag


class DatabasePathForm(forms.Form):
    database_path = forms.CharField(
        label="Database Folder",
        help_text="Select a folder. The current database will be copied there.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_database_path(self):
        from django.conf import settings

        path = os.path.abspath(os.path.expanduser(self.cleaned_data["database_path"].strip()))
        if not path:
            raise forms.ValidationError("Database path cannot be empty.")
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if os.path.splitext(path)[1].lower() in {".sqlite3", ".sqlite", ".db"} and not os.path.isdir(path):
            raise forms.ValidationError("Select a folder. The database file will be copied into it automatically.")
        current_name = os.path.basename(str(settings.DATABASES["default"]["NAME"]))
        return os.path.join(path, current_name)


class MediaRootForm(forms.Form):
    media_root = forms.CharField(
        label="Media Root",
        help_text="Select a folder. Existing media files will be copied there.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_media_root(self):
        path = os.path.abspath(os.path.expanduser(self.cleaned_data["media_root"].strip()))
        if not path:
            raise forms.ValidationError("Media root cannot be empty.")
        if not os.path.isabs(path):
            raise forms.ValidationError("Media root must be absolute.")
        if os.path.isfile(path):
            raise forms.ValidationError("Media root must be a directory path, not a file.")
        return path


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'tags', 'color', 'referenced_items']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'referenced_items': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['referenced_items'].queryset = Item.objects.exclude(pk=self.instance.pk)
        else:
            self.fields['referenced_items'].queryset = Item.objects.all()

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tag name"}),
            "color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }


class CustomFilterForm(forms.ModelForm):
    class Meta:
        model = CustomFilter
        fields = ["name", "items"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Filter name"}),
            "items": forms.SelectMultiple(attrs={"class": "form-select", "size": 12}),
        }


class StyledUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs.pop("autofocus", None)
