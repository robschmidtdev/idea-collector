from django import forms
from .models import CustomFilter, Item, Tag


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'tags', 'color', 'referenced_items']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
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