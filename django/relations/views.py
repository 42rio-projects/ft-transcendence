from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from pong.utils import render_component
from user.models import User, FriendInvite


def friends(request):
    if request.method == 'POST':
        # Remove friend
        user_id = request.POST.get('user-id')
        user = get_object_or_404(User, pk=user_id)
        request.user.del_friend(user)

    return render_component(request, 'friends.html', 'content')


def friend_invites_sent(request):
    if request.method == 'POST':
        # Cancel friend invite
        invite_id = request.POST.get('invite-id')
        invite = get_object_or_404(FriendInvite, pk=invite_id)
        if invite.sender != request.user:
            raise PermissionDenied
        invite.delete()

    return render_component(request, 'friend_invites_sent.html', 'content')


def friend_invites_received(request):
    if request.method == 'POST':
        # Accept/Reject friend invite
        invite_id = request.POST.get('invite-id')
        invite = get_object_or_404(FriendInvite, pk=invite_id)
        if invite.receiver != request.user:
            raise PermissionDenied
        user_action = request.POST.get('user-action')
        if user_action == 'accept':
            invite.respond(accepted=True)
        elif user_action == 'reject':
            invite.respond(accepted=False)

    return render_component(request, 'friend_invites_received.html', 'content')


def block_list(request):
    if request.method == 'POST':
        # Unblock user
        user_id = request.POST.get('user-id')
        user = get_object_or_404(User, pk=user_id)
        request.user.unblock_user(user)

    return render_component(request, 'block_list.html', 'content')


def send_friend_invites(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('username')
            user = get_object_or_404(User, username=name)
            request.user.add_friend(user)

            return render_component(request, 'send_friend_invites.html', 'content', {
                'success': 'Friend invite sent!'
            })
        except Exception as e:
            if type(e) == Http404:
                error = 'User not found'
            else:
                error = e.message

            return render_component(request, 'send_friend_invites.html', 'content', {
                'username': name, # So user doesn't have to re-type the username
                'error': error
            })

    return render_component(request, 'send_friend_invites.html', 'content')


def block_user(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('username')
            user = get_object_or_404(User, username=name)
            request.user.block_user(user)
            return render_component(request, 'block_user.html', 'content', {
                'success': 'User blocked!'
            })
        except Exception as e:
            if type(e) == Http404:
                error = 'User not found'
            else:
                error = e.message

            return render_component(request, 'block_user.html', 'content', {
                'username': name, # So user doesn't have to re-type the username
                'error': error
            })

    return render_component(request, 'block_user.html', 'content')
