from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import BottleServiceUser


class BottleServiceUserCreationForm(UserCreationForm):

    class Meta:
        model = BottleServiceUser
        fields = ("email", "account_type")


class BottleServiceUserChangeForm(UserChangeForm):

    class Meta:
        model = BottleServiceUser
        fields = ("email", "account_type")