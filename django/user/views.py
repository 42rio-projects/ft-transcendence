from django.shortcuts import redirect, render
from pong.utils import render_component
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from twilio.rest import Client
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib import messages
import os

from user.models import User
from user.forms import EmailChangeForm
from user.forms import ChangePasswordForm
from user.forms import UserProfileForm

from .utils import validate_register

SERVICE_SID = os.environ["TWILIO_SERVICE_SID"]
ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        errors_context = validate_register(username, password, password2)
        if errors_context:
            # Add the previous values to the context
            # So the user doesn't have to retype everything
            errors_context["username"] = username
            errors_context["password"] = password
            errors_context["password2"] = password2

            return render_component(request, "auth/register_form_fields.html", "form-fields", errors_context, 400)

        User.objects.create_user(username=username, password=password)

        messages.success(request, "Registered! You can now login.")
        return redirect("login")

    if request.method == "GET":
        return render_component(request, "auth/register.html", "body")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            context = {
                "username": username,
                "password": password,
                "error": "Incorrect username or password"
            }

            return render_component(request, "auth/login_form_fields.html", "form-fields", context, 400)

        django_login(request, user)
        return redirect("home")

    if request.method == "GET":
        return render_component(request, "auth/login.html", "body")


def logout(request):
    if request.method == "GET":
        django_logout(request)
        messages.success(request, "Logged out.")
        return redirect("home")


def profile(request):
    if request.method == "GET":
        return render(request, "profile.html")


@login_required
def upload_avatar(request):
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'upload_avatar.html', {'form': form})


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        email_verified = request.user.email_verified
        if not email_verified:
            messages.error(
                request,
                "You must verify your email before changing your password"
            )
            return render(request, "change_password.html", {"form": form})
        if form.is_valid():
            user = request.user
            current_password = form.cleaned_data.get("current_password")
            if (user.check_password(current_password)):
                new_password = form.cleaned_data.get("new_password")
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully")
            else:
                form.add_error('current_password', "Senha atual incorreta")

    if request.method == 'GET':
        form = ChangePasswordForm()
    return render(request, "change_password.html", {"form": form})


def email_change(request):

    if request.method == "GET":
        form = EmailChangeForm()
        return render(request, "email_change_form.html", {"form": form})

    if request.method == "POST":
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            newEmail = form.cleaned_data.get("new_email")
            if User.objects.filter(email=newEmail).exists():
                messages.error(request, "Email already in use")
                return render(request, "email_change_form.html", {"form": form})
            request.session['new_email'] = newEmail

            verification = Client(ACCOUNT_SID, AUTH_TOKEN).verify.v2.services(
                SERVICE_SID).verifications.create(to=newEmail, channel="email")

            if verification.status == "pending":
                messages.success(
                    request,
                    f'Um código de verificação foi enviado para o email {newEmail}.'
                )
                return render(request, "email_change_check_form.html")

        messages.error(request, 'Dados inválidos.')
        form = EmailChangeForm()
        return render(request, "email_change_form.html", {"form": form})


def email_change_check(request):

    code = request.POST.get("code")
    newEmail = request.session.get('new_email')
    verification = Client(ACCOUNT_SID, AUTH_TOKEN).verify.v2.services(
        SERVICE_SID).verification_checks.create(to=newEmail, code=code)

    if verification.status == "approved":
        user = request.user
        user.email = newEmail
        user.email_verified = True
        user.save()
        messages.success(request, 'Seu e-mail foi atualizado com sucesso.')
        return redirect("profile")

    messages.error(request, 'Código de verificação inválido.')
    return render(request, "email_change_check_form.html")


def edit_profile(request):
    if request.method == "POST":
        user = request.user
        username = request.POST.get("username")

        if username != user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already in use")
            elif len(username) < 3:
                messages.error(
                    request, "Username must be at least 3 characters")
            else:
                user.username = username

                messages.success(request, "Username changed successfully")

        if not user.email_verified:
            email = request.POST.get("email")

            if email != user.email:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already in use")
                elif len(email) < 3:
                    messages.error(
                        request, "Email must be at least 3 characters")
                else:
                    user.email = email
                    user.email_verified = False

                    messages.success(request, "Email changed successfully")

        user.save()

        return render(
            request,
            "edit_profile.html",
            {"username": user.username, "email": user.email}
        )

    if request.method == "GET":
        return render(
            request,
            "edit_profile.html",
            {"username": request.user.username, "email": request.user.email}
        )


def email_verify_code(request):
    if request.method == "GET":
        user = request.user

        verification = Client(ACCOUNT_SID, AUTH_TOKEN).verify.v2.services(
            SERVICE_SID).verifications.create(to=user.email, channel="email")

        status = verification.status

        if status == "pending":
            messages.success(request, "Verification code sent to your email!")
            return render(request, "email_verify_check_form.html")

        messages.error(request, "Error sending verification code")
        return render(request, "profile.html")


def email_verify_check(request):
    if request.method == "POST":
        user = request.user
        code = request.POST.get("code")

        verification = Client(ACCOUNT_SID, AUTH_TOKEN).verify.v2.services(
            SERVICE_SID).verification_checks.create(to=user.email, code=code)

        status = verification.status

        print("Status value: ", status)

        if status == "approved":
            user.email_verified = True
            user.save()

            messages.success(request, "Email verified!")
            return redirect("profile")

        messages.error(request, "Wrong verification code")
        return render(request, "email_verify_check_form.html")
