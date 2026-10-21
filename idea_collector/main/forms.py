from django import forms
from .models import Item, Tag

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tag name"}),
            "color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }