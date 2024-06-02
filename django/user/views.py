from django.shortcuts import redirect, get_object_or_404
from pong.utils import render_component
from twilio.rest import Client
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
import os
from django.core.paginator import Paginator
import sys
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.http import HttpResponse
from user.models import User
from pong.models import Tournament
from .utils import validate_password, validate_register

SERVICE_SID = os.environ['TWILIO_SERVICE_SID']
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
SERVICE_SID = os.environ["TWILIO_SERVICE_SID"]

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def history(request, username):
    user = get_object_or_404(User, username=username)
    context = {'user': user}
    return render_component(request, 'history/index.html', 'content', context)


def match_history(request, username):
    user = get_object_or_404(User, username=username)
    return render_component(
        request,
        'history/match.html',
        'content',
        {'user': user}
    )


def tournament_history(request, username):
    user = get_object_or_404(User, username=username)
    return render_component(
        request,
        'history/tournament.html',
        'content',
        {'user': user}
    )


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
        return redirect(request.GET.get('next') or '/')

    if request.method == 'GET':
        return render_component(request, 'login.html', 'content')


def logout(request):
    if request.method == 'GET':
        django_logout(request)
        return redirect('/')


@login_required
def my_profile(request):
    if request.method == 'GET':
        return render_component(request, 'profile.html', 'content')


def user_profile(request, username):
    if username == request.user.username:
        return redirect('/profile/')

    user = get_object_or_404(User, username=username)
    context = {'user': user}

    if request.method == 'POST':
        user_action = request.POST.get('user-action')
        try:
            if user_action == 'send-friend-invite':
                request.user.add_friend(user)
                context['success'] = 'Friend invite sent'
            elif user_action == 'cancel-friend-invite':
                request.user.cancel_friend_invite(user)
                context['success'] = 'Friend invite canceled'
            elif user_action == 'remove-friend':
                request.user.del_friend(user)
                context['success'] = 'Friendship removed!'
            elif user_action == 'game-invite':
                try:
                    game = request.user.invite_to_game(user)
                    return redirect('onlineGame', game_id=game.pk)
                except Exception as e:
                    context['error'] = e.message
            elif user_action == 'block':
                request.user.block_user(user)
                context['success'] = 'User blocked'
            elif user_action == 'unblock':
                request.user.unblock_user(user)
                context['success'] = 'User unblocked'
            elif user_action == 'send-message':
                chat = request.user.get_or_create_chat(user)
                return redirect('chatRoom', id=chat.pk)
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

def change_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = request.user

        try :
            if email != user.email:
                user.change_email(email)
                return render_component(request, 'change_email_form.html', 'form', {
                    'success': 'Email changed successfully!'
                })

        except Exception as e:
            return render_component(request, 'change_email_form.html', 'form', {
                'error': e,
                'email': email
            }, 400)


    if request.method == 'GET':
        return render_component(request, 'change_email.html', 'content')

def verify_email(request):
    user = request.user
    if request.method == 'POST':

        code = request.POST.get('code')

        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        verification_check = client.verify.services(
            SERVICE_SID).verification_checks.create(to=user.email, code=code)

        if verification_check.status != 'approved':
            return render_component(request, 'verify_email_forms.html', 'forms', {
                'error': 'Invalid code'
            })

        user.email_verified = True
        user.save()
        return render_component(request, 'verify_email_forms.html', 'forms', {
            'success': 'Email verified successfully!'
        })

    if request.method == 'GET':

            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            client.verify.services(SERVICE_SID).verifications.create(
                to=user.email, channel='email')

            return render_component(request, 'verify_email.html', 'content', {
                'message': 'Verification code sent to your email'
            })
