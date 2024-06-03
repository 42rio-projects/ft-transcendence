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
from .utils import validate_password, validate_register, validate_update, handle_user_action

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
    if request.user.is_authenticated:
        return redirect('/')

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
            return render_component(request, 'register/form.html', 'form', errors_context, 400)
        else:
            User.objects.create_user(username=username, password=password)
            return render_component(request, 'register/form.html', 'form', {
                'success': 'User created successfully!'
            })
    return render_component(request, 'register/index.html', 'content')


def login(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or '/')

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
            return render_component(request, 'login/form.html', 'form', context, 400)
        else:
            django_login(request, user)
            return redirect(request.GET.get('next') or '/')
    return render_component(request, 'login/index.html', 'content')


@login_required
def logout(request):
    django_logout(request)
    return redirect('/')


@login_required
def my_profile(request):
    return render_component(request, 'profile.html', 'content')


@login_required
def user_profile(request, username):
    if username == request.user.username:
        return redirect('/profile/')

    user = get_object_or_404(User, username=username)
    context = { 'user': user }

    if request.method == 'POST':
        action = request.POST.get('user-action')
        try:
            if action == 'game-invite':
                game = request.user.invite_to_game(user)
                return redirect('onlineGame', game_id=game.pk)
            elif action == 'send-message':
                chat = request.user.get_or_create_chat(user)
                return redirect('chatRoom', id=chat.pk)
            else:
                context['success'] = handle_user_action(request.user, user, action)
        except Exception as e:
            context['error'] = e.message
            return render_component(request, 'profile.html', 'content', context, 400)
    return render_component(request, 'profile.html', 'content', context)


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        avatar = request.FILES.get('avatar')

        errors_context = validate_update(user, username, nickname)
        if errors_context:
            errors_context.update({
                'username': username,
                'nickname': nickname or '' # Set to empty string if None, so it can be rendered in template
            })
            return render_component(request, 'edit_profile.html', 'content', errors_context, 400)
        else:
            user.username = username
            user.nickname = nickname or None # Set to None if empty string, so it's null in database
            if avatar:
                user.avatar = avatar
            user.save()
            return render_component(request, 'edit_profile.html', 'content', {
                'success': 'Profile saved!',
                'username': user.username,
                'email': user.email,
                'nickname': user.nickname or ''
            })
    return render_component(request, 'edit_profile.html', 'content', {
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname or ''
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
