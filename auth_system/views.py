from django.shortcuts import render, redirect
from . import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from . import models


def register_view(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password == confirm_password:
                created_user = models.CustomUser.objects.create(first_name=first_name,
                                    last_name=last_name,
                                    email=email,
                                    username=username,
                                    password=make_password(password))
                    
                created_user.save()

                user = authenticate(request, username=username, password=password)

                if user:
                    login(request, user)

                    return redirect("task-list")
                else:
                    messages.error(request, "Автентифікація не пройшла. Спробуйте ще раз.")
            else:
                messages.warning(request=request,
                                message="Паролі не співпадають. Спробуйте ще раз.")
        else:
            messages.error(request=request, 
                           message="Форма недійсна. Будь ласка, виправте помилки.")
    else:
        form = forms.RegisterForm()

    return render(request, "auth_system/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request=request,
                                username=username,
                                password=password)
            
            if user:
                login(request, user)

                return redirect("task-list")
            else:
                messages.warning(request=request,
                                 message="Неправильне ім'я користувача або пароль. Спробуйте ще раз.")
        else:
            messages.error(request=request, 
                           message="Форма недійсна. Будь ласка, виправте помилки.")
    else:
        form = forms.LoginForm()

    return render(request, "auth_system/login.html", {"form": form})
        

def logout_view(request):
    logout(request)

    return redirect("task-list")

def profile_view(request):
    return render(request, "auth_system/profile.html")

def edit_profile_view(request):
    if request.method == "POST":
        form = forms.EditProfileForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            new_password = form.cleaned_data["new_password"]
            old_password = form.cleaned_data["old_password"]
            about_user = form.cleaned_data["about_user"]
            avatar = form.cleaned_data["avatar"]
    
            user = models.CustomUser.objects.get(username=request.user.username)

            if user and user.check_password(old_password):
                if new_password:
                    user.set_password(new_password)
                    login(request, user)

                if first_name:
                    user.first_name = first_name

                if last_name:
                    user.last_name = last_name
                    
                if email:
                    user.email = email

                if username:
                    user.username = username

                if about_user:
                    user.bio = about_user

                if avatar:
                    user.avatar = avatar
                
                user.save()

                return redirect("profile")
            else:
                messages.error(request, "Старий пароль невірний. Спробуйте ще раз.")
        else:
            messages.error(request, "Форма недійсна. Будь ласка, виправте помилки.")
    else:
        form = forms.EditProfileForm()

    return render(request, "auth_system/profile-form.html", {"form": form})

def delete_account_view(request):
    if request.method == "POST":
        form = forms.DeleteAccountForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]

            user = authenticate(request, username=request.user.username, password=password)

            if user:
                logout(request)
                user.delete()

                return redirect("task-list")
            else:
                messages.error(request, "Пароль невірний. Спробуйте ще раз.")
        else:
            messages.error(request, "Форма недійсна. Будь ласка, виправте помилки.")
    else:
        form = forms.DeleteAccountForm()

    return render(request, "auth_system/profile-form.html", {"form": form})