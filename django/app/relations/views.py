from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied

import relations.models as models
from user.models import User


def friends(request):
    template = loader.get_template('relations/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def friendlist(request):
    template = loader.get_template("relations/friendlist.html")
    context = {}
    return HttpResponse(template.render(context, request))


def friendInvitesSent(request):
    template = loader.get_template("relations/invites_sent.html")
    context = {}
    return HttpResponse(template.render(context, request))


def friendInvitesReceived(request):
    template = loader.get_template("relations/invites_received.html")
    context = {}
    return HttpResponse(template.render(context, request))


def blocklist(request):
    template = loader.get_template("relations/blocklist.html")
    context = {}
    return HttpResponse(template.render(context, request))


def sendFriendInvites(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            request.user.add_friend(user)
            # add 201 response that is not rendered on the front end
        except Exception as e:
            # add 40x response that is not rendered on the front end
            return HttpResponse(e)
    template = loader.get_template("relations/send_invites.html")
    context = {}
    return HttpResponse(template.render(context, request))


def blockUser(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            request.user.block_user(user)
            # add 201 response that is not rendered on the front end
        except Exception as e:
            # add 40x response that is not rendered on the front end
            return HttpResponse(e)
    template = loader.get_template("relations/block_user.html")
    context = {}
    return HttpResponse(template.render(context, request))


def excludeFriend(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(
            User,
            pk=user_id,
        )
        try:
            request.user.del_friend(user)
        except Exception as e:
            return HttpResponse(e)
    return redirect('friendList')


def unblockUser(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(
            User,
            pk=user_id,
        )
        try:
            request.user.unblock_user(user)
        except Exception as e:
            return HttpResponse(e)
    return redirect('blockList')


def respondFriendInvite(request, invite_id):
    invite = get_object_or_404(
        models.FriendInvite,
        pk=invite_id,
    )
    if invite.receiver != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            invite.respond(accepted=True)
        elif action == 'reject':
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
    return redirect('friendInvitesReceived')


def cancelFriendInvite(request, invite_id):
    if request.method == 'POST':
        invite = get_object_or_404(
            models.FriendInvite,
            pk=invite_id,
        )
        if invite.sender != request.user:
            raise PermissionDenied
        invite.delete()
    return redirect('friendInvitesSent')
