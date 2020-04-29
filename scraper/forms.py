from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import User, MoodleDetails


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField()
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"class":""}))
    password2 = forms.CharField(label=_("Password Again"),widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")


class MoodleDetailsForm(forms.ModelForm):
    matric_num = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = MoodleDetails
        fields = ("matric_num", "password")

