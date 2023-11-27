# myapp/forms.py
from django import forms
from .models import Address, Distributor


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'city', 'state', 'zip']


class DistributorForm(forms.ModelForm):
    class Meta:
        model = Distributor
        fields = ['name', 'description']
