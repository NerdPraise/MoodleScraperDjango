from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
    matric_num = forms.CharField(widget=forms.TextInput(attrs={'class': "w3-input w3-border w3-margin-bottom w3-round", "placeholder":"Matric Number"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"w3-input w3-border w3-round","placeholder":"Password"}))

    class Meta:
        model = MoodleDetails
        fields = ("matric_num", "password")

class SignInForm(AuthenticationForm):
    
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"class":""}))

    class Meta:
        model = User
        
    
