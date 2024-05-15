from django.shortcuts import redirect, get_object_or_404
from pong.utils import render_component
from twilio.rest import Client
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
import os
from user.models import User
from .utils import validate_password, validate_register, validate_update

SERVICE_SID = os.environ['TWILIO_SERVICE_SID']
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']


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

    if request.method == 'GET':
        return render_component(request, 'profile.html', 'content', context)


def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        username = request.POST.get('username')
        email = request.POST.get('email')

        if not avatar and username == user.username and email == user.email:
            # Nothing changed
            return render_component(request, 'edit_profile_form.html', 'form', {
                'username': user.username,
                'email': user.email,
            })

        errors_context = validate_update(user, username, email)
        if errors_context:
            errors_context['username'] = username
            errors_context['email'] = email

            return render_component(request, 'edit_profile_form.html', 'form', errors_context, 400)

        if avatar:
            user.avatar = avatar

        if username != user.username:
            user.username = username

        if email != user.email:
            user.email = email
            user.email_verified = False

        user.save()

        return render_component(request, 'edit_profile.html', 'content', {
            'success': 'Profile saved!',
            'username': user.username,
            'email': user.email,
        })

    if request.method == 'GET':
        return render_component(request, 'edit_profile.html', 'content', {
            "username": user.username,
            "email": user.email
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
