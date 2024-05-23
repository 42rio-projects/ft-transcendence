from django.shortcuts import redirect, get_object_or_404
from pong.utils import render_component
from twilio.rest import Client
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
import os
from django.core.paginator import Paginator
import sys

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponse
from user.models import User
from pong.models import Tournament
from .utils import validate_password, validate_register, validate_update

SERVICE_SID = os.environ['TWILIO_SERVICE_SID']
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
SERVICE_SID = os.environ["TWILIO_SERVICE_SID"]

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def match_history(request):
    if request.method == "GET":
        games_list = request.user.get_games()
        paginator = Paginator(games_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render_component(request, 'match_history/index.html', 'content', {'page_obj': page_obj})

def tournament_history(request):
    if request.method == "GET":
        tournaments_list = Tournament.get_tournaments_by_user(request.user)
        print(tournaments_list, file=sys.stderr)
        paginator = Paginator(tournaments_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render_component(request, 'tournament_history/index.html', 'content', {'page_obj': page_obj})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        errors_context = validate_register(username, password, password2)
        if errors_context:
            # Add the previous values to the context
            # So the user doesn't have to retype everything
            errors_context.update({
                'username': username,
                'password': password,
                'password2': password2
            })

            return render_component(request, 'register_form.html', 'form', errors_context, 400)

        User.objects.create_user(username=username, password=password)
        return render_component(request, 'register_form.html', 'form', {
            'success': 'User created successfully!'
        })

    if request.method == 'GET':
        return render_component(request, 'register.html', 'content')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            context = {
                'username': username,
                'password': password,
                'error': 'Incorrect username or password'
            }

            return render_component(request, 'login_form.html', 'form', context, 400)

        django_login(request, user)
        return redirect('/')

    if request.method == 'GET':
        return render_component(request, 'login.html', 'content')


def logout(request):
    if request.method == 'GET':
        django_logout(request)
        return redirect('/')


def my_profile(request):
    if request.method == 'GET':
        return render_component(request, 'profile.html', 'content')


def user_profile(request, username):
    if username == request.user.username:
        return redirect('/profile/')

    user = get_object_or_404(User, username=username)
    context = { 'user': user }

    if request.method == 'POST':
        user_action = request.POST.get('user-action')
        try:
            if user_action == 'friend-invite':
                request.user.add_friend(user)
                context['success'] = 'Friend invite sent'
            elif user_action == 'block':
                request.user.block_user(user)
                context['success'] = 'User blocked'
        except Exception as e:
            context['error'] = e.message

        return render_component(request, 'profile.html', 'content', context)

    if request.method == 'GET':
        return render_component(request, 'profile.html', 'content', context)


def edit_profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")

        try:
            if (username != user.username):
                user.change_username(username)

            if (nickname != user.nickname):
                user.change_nickname(nickname)

            if email != user.email:
                user.change_email(email)

        except Exception as e:
            return render_component(request, 'edit_profile.html', 'content', {
                'error': e,
                'username': username,
                'email': email,
                'nickname': nickname
            }, 400)

        return render_component(request, 'edit_profile.html', 'content', {
            'success': 'Profile saved!',
            'username': user.username,
            'email': user.email,
            'nickname': user.nickname,
        })

    if request.method == 'GET':
        return render_component(request, 'edit_profile.html', 'content', {
            "username": user.username,
            "email": user.email,
            'nickname': user.nickname
        })

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

def change_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        errors_context = validate_password(password, password2)
        if errors_context:
            errors_context['password'] = password
            errors_context['password2'] = password2

            return render_component(request, 'change_password_form.html', 'form', errors_context, 400)

        request.user.set_password(password)

        return render_component(request, 'change_password_form.html', 'form', {
            'success': 'Password changed successfully!'
        })

    if request.method == 'GET':
        return render_component(request, 'change_password.html', 'content')


def verify_email(request):
    if request.method == 'POST':
        user = request.user
        user_action = request.POST.get('user-action')

        if user_action == 'send-code':
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            client.verify.services(SERVICE_SID).verifications.create(to=user.email, channel='email')

            return render_component(request, 'verify_email_forms.html', 'forms', {
                'success': 'Verification code sent to your email'
            })
        elif user_action == 'verify-code':
            code = request.POST.get('code')

            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            verification_check = client.verify.services(SERVICE_SID).verification_checks.create(to=user.email, code=code)

            if verification_check.status != 'approved':
                return render_component(request, 'verify_email_forms.html', 'forms', {
                    'error': 'Invalid code'
                })

            user.email_verified = True
            user.save()
            return render_component(request, 'verify_email_forms.html', 'forms', {
                'success': 'Email verified successfully!'
            })

        return render_component(request, 'verify_email_forms.html', 'forms')

    if request.method == 'GET':
        return render_component(request, 'verify_email.html', 'content')
