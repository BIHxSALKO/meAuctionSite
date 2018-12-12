from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from crispy_forms.bootstrap import PrependedText, FormActions
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Watchlist

class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name', 'start_price']
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class CheckoutCart(forms.Form):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        FormActions(Submit('Checkout Cart', 'Checkout Cart')))