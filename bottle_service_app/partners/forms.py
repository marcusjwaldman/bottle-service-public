from django import forms
from .models import MenuItem, MenuItemCategory


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'distributor_notes', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = MenuItemCategory.objects.all()

        # Customize the widget for the 'your_field' to be a Select widget
        self.fields['category'].widget = forms.Select(attrs={'class': 'your-css-class'})
        self.fields['category'].choices = [(category.id, category.name) for category in categories]
