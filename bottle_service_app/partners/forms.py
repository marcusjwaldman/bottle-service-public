from django import forms
from .models import Item, MenuItemCategory


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'distributor_notes', 'category']

    distributor_notes = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = MenuItemCategory.objects.all()

        # Customize the widget for the 'your_field' to be a Select widget
        self.fields['category'].widget = forms.Select(attrs={'class': 'your-css-class'})
        self.fields['category'].choices = [(category.id, category.name) for category in categories]
