from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomFilter, Item, Tag


class DatabasePathForm(forms.Form):
    database_path = forms.CharField(
        label="Database Path",
        help_text="Absolute path to the SQLite database file.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class MediaRootForm(forms.Form):
    media_root = forms.CharField(
        label="Media Root",
        help_text="Absolute path where uploaded media files are stored.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


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
