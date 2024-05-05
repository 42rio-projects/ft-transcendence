from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from pong.utils import render_component
from user.models import User, FriendInvite


def friends_index(request):
    return render_component(request, 'friends_index.html', 'body')


def friend_list(request):
    return render_component(request, 'friend_list.html', 'body')


def remove_friend(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    request.user.del_friend(user)
    return render_component(request, 'friend_list.html', 'body')


def friend_invites_sent(request):
    return render_component(request, 'friend_invites_sent.html', 'body')


def send_friend_invites(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('username')
            user = get_object_or_404(User, username=name)
            request.user.add_friend(user)

            return render_component(request, 'send_friend_invites.html', 'body', {
                'success': 'Friend invite sent!'
            })
        except Exception as e:
            if type(e) == Http404:
                error = 'User not found'
            else:
                error = e.message

            return render_component(request, 'send_friend_invites.html', 'body', {
                'username': name, # So user doesn't have to re-type the username
                'error': error
            })

    return render_component(request, 'send_friend_invites.html', 'body')


def cancel_friend_invite(request, invite_id):
    invite = get_object_or_404(FriendInvite, pk=invite_id)
    if invite.sender != request.user:
        raise PermissionDenied
    invite.delete()
    return render_component(request, 'friend_invites_sent.html', 'body')


def friend_invites_received(request):
    return render_component(request, 'friend_invites_received.html', 'body')


def respond_friend_invite(request, invite_id):
    invite = get_object_or_404(FriendInvite, pk=invite_id)
    if invite.receiver != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        user_action = request.POST.get('user-action')
        if user_action == 'accept':
            invite.respond(accepted=True)
        elif user_action == 'reject':
            invite.respond(accepted=False)

    return render_component(request, 'friend_invites_received.html', 'body')


def block_list(request):
    return render_component(request, 'block_list.html', 'body')


def block_user(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('username')
            user = get_object_or_404(User, username=name)
            request.user.block_user(user)
            return render_component(request, 'block_user.html', 'body', {
                'success': 'User blocked!'
            })
        except Exception as e:
            if type(e) == Http404:
                error = 'User not found'
            else:
                error = e.message

            return render_component(request, 'block_user.html', 'body', {
                'username': name, # So user doesn't have to re-type the username
                'error': error
            })

    return render_component(request, 'block_user.html', 'body')


def unblock_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        request.user.unblock_user(user)

    return render_component(request, 'block_list.html', 'body')
