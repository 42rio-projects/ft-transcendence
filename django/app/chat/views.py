from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from pong.utils import render_component

import chat.models as models


def check_permissions_and_get_other_user(chat, user):
    if chat.starter != user and chat.receiver != user:
        raise Exception('Not your chat')
    other_user = chat.receiver if chat.starter == user else chat.starter
    if other_user in user.get_blocks():
        raise Exception('This user was blocked')
    return other_user


def chatRoom(request, id):
    chat = get_object_or_404(models.Chat, pk=id)
    try:
        other_user = check_permissions_and_get_other_user(chat, request.user)
    except Exception as e:
        return HttpResponseForbidden(e.__str__())

    if other_user == request.user:
        return redirect('notifications')
    if request.user in other_user.get_blocks() or other_user in request.user.get_blocks():
        return redirect('userProfile', other_user.username)
    if request.method == 'POST':
        try:
            game = request.user.invite_to_game(other_user)
            return redirect('onlineGame', game_id=game.pk)
        except Exception:
            return redirect('userProfile', other_user.username)

    context = {"chat": chat, "other_user": other_user}
    return render_component(request, 'chat/chat.html', 'content', context)


def sendMessage(request, id):
    if request.method == 'GET':
        return redirect('chatRoom', id=id)
    try:
        chat = models.Chat.objects.get(pk=id)
    except Exception:
        return JsonResponse({"status": "error", "msg": "Chat does not exist"})
    try:
        other_user = check_permissions_and_get_other_user(chat, request.user)
    except Exception as e:
        return JsonResponse({"status": "error", "msg": e.__str__()})

    if request.method == 'POST':
        if request.user in other_user.get_blocks():
            return JsonResponse(
                {"status": "error", "msg": "This user blocked you"}
            )
        content = request.POST.get('content')
        try:
            message = models.Message(
                content=content, sender=request.user, chat=chat
            )
            message.save()
            return JsonResponse({"status": "success", "id": message.id})
        except Exception:
            return JsonResponse(
                {"status": "error", "msg": "Failed to send message"}
            )


def notifications(request):
    chat = request.user.get_or_create_notifications()
    context = {"chat": chat, "other_user": request.user}
    return render_component(request, 'chat/chat.html', 'content', context)
