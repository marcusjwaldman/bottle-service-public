from django import forms

from customer.models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['last_name', 'first_name', 'email']
        