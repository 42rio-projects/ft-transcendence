from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from twilio.rest import Client
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib import messages
from django.shortcuts import render
import os
from django.core.paginator import Paginator

from django.http import JsonResponse
from django.http import HttpResponse
from user.models import User
from user.forms import EmailChangeForm
from user.forms import ChangePasswordForm
from user.forms import UserProfileForm

SERVICE_SID = os.environ["TWILIO_SERVICE_SID"]
ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(ACCOUNT_SID, AUTH_TOKEN)


def profile(request):
    if request.method == "GET":
        return render(request, "profile.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Incorrect username or password")
            return render(request, "login.html",
                          {"username": username,
                           "password": password})

        django_login(request, user)
        messages.success(request, "You are now logged in")
        return redirect("main")

    if request.method == "GET":
        return render(request, "login.html")

def match_history(request):
    if request.method == "GET":
        games_list = request.user.get_games()
        paginator = Paginator(games_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'match_history/index.html', {'page_obj': page_obj})

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        context = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password
        }

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already in use")
            return render(request, "register.html", context)

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html", context)

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(request, "register.html", context)

        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "You are now registered and can log in")
        return redirect("login")

    if request.method == "GET":
        return render(request, "register.html")


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


def logout(request):
    if request.method == "GET":
        django_logout(request)
        messages.success(request, "You are now logged out")
        return render(request, "logout.html")


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

# @login_required
def generate_totp_factor(request):
    if request.method == "GET":
        # user = request.user

        # new_factor = client.verify.v2.services(
        #     SERVICE_SID).entities(user.id).new_factors.create(
        #     friendly_name=user.name, factor_type="totp")
        new_factor = client.verify.v2.services(
            SERVICE_SID).entities('ff483d1ff591898a9942916050d2ca3f').new_factors.create(
            friendly_name='Vitinho', factor_type="totp")

        serialized_factor = serialize_factor(new_factor)

        return JsonResponse(serialized_factor, safe=False)


# @login_required
def verify_totp_factor(request):
    if request.method == "POST":
        # user = request.user

        code = request.POST.get("code")
        sid = request.POST.get("sid")

        # factor = client.verify.v2.services(
        #     SERVICE_SID).entities(user.id).factors(sid).update(auth_payload=code)
        factor = client.verify.v2.services(
            SERVICE_SID).entities('ff483d1ff591898a9942916050d2ca3f').factors(sid).update(auth_payload=code)

        status = factor.status

        if status == "approved":
           return HttpResponse("Factor is valid")

        return HttpResponse("Factor is invalid")

def serialize_factor(factor):
    serialized_data = {
        'sid': factor.sid,
        'status': factor.status,
        'identity': factor.identity,
        'friendly_name': factor.friendly_name,
    }
    return serialized_data

# @login_required
def list_totp_factors(request):
    if request.method == "GET":
        # user = request.user

        # factors = client.verify.v2.services(
        #     SERVICE_SID).entities(user.id).factors.list()
        factors = client.verify.v2.services(
            SERVICE_SID).entities('ff483d1ff591898a9942916050d2ca3f').factors.list()

        serialized_factors =  [serialize_factor(factor) for factor in factors]

        return JsonResponse(serialized_factors, safe=False)

def validate_totp_token(request):
    if request.method == "POST":
        # user = request.user

        token = request.POST.get("token")
        sid = request.POST.get("sid")

        # verification = client.verify.v2.services(
        #     SERVICE_SID).entities(user.id).challenges.create(
        #     factor_sid=sid,
        #     code=token
        # )
        verification = client.verify.v2.services(
            SERVICE_SID).entities('ff483d1ff591898a9942916050d2ca3f').challenges.create(
            factor_sid=sid,
            auth_payload=token
        )

        status = verification.status

        if status == "approved":
            return HttpResponse("Token is valid")

        return HttpResponse("Token is invalid")

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
