from django import forms
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Ім'я користувача")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="Ім'я")  
    last_name = forms.CharField(max_length=100, label="Прізвище")
    email = forms.EmailField(label="Електронна пошта")
    username = forms.CharField(max_length=50, label="Ім'я користувача")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Підтвердження пароля")

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False, label="Ім'я")
    last_name = forms.CharField(max_length=100, required=False, label="Прізвище")
    email = forms.EmailField(required=False, label="Електронна пошта")
    username = forms.CharField(max_length=50, required=False, label="Ім'я користувача")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Новий пароль")
    old_password = forms.CharField(widget=forms.PasswordInput, label="Старий пароль")
    about_user = forms.CharField(widget=forms.Textarea, required=False, label="Про мене")
    avatar = forms.FileField(required=False, label="Аватар")
    
class DeleteAccountForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    