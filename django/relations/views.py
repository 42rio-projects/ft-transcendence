from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
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
