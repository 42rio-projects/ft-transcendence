from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from pong.utils import render_component

from user.models import User
import chat.models as models


def check_permissions_and_get_other_user(chat, user):
    if chat.starter != user and chat.receiver != user:
        raise Exception('Not your chat')
    other_user = chat.receiver if chat.starter == user else chat.starter
    if other_user in user.get_blocks():
        raise Exception('This user was blocked')
    return other_user


def chatIndex(request):
    template = loader.get_template('chat/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def chatList(request):
    template = loader.get_template('chat/chatlist.html')
    context = {}
    return HttpResponse(template.render(context, request))


def chatRoom(request, id):
    chat = get_object_or_404(models.Chat, pk=id)
    try:
        other_user = check_permissions_and_get_other_user(chat, request.user)
    except Exception as e:
        return HttpResponseForbidden(e.__str__())

    if request.method == 'POST':
        game = request.user.invite_to_game(other_user)
        return redirect('onlineGame', game_id=game.pk)

    context = {"chat": chat, "other_user": other_user}
    return render_component(request, 'chat/chat.html', 'content', context)


# Colocar para retornar JSON
def sendMessage(request, id):
    chat = get_object_or_404(models.Chat, pk=id)
    try:
        other_user = check_permissions_and_get_other_user(chat, request.user)
    except Exception as e:
        return HttpResponseForbidden(e.__str__())

    if request.method == 'POST':
        if request.user in other_user.get_blocks():
            return HttpResponseForbidden('This user blocked you')
        content = request.POST.get('content')
        try:
            message = models.Message(
                content=content, sender=request.user, chat=chat
            )
            message.save()
            return JsonResponse({"id": message.id})
        except Exception as e:
            return HttpResponse(e)


def startChat(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            models.Chat(starter=request.user, receiver=user).save()
            # add 201 response that is not rendered on the front end
        # except ValidationError as e:
            # return HttpResponse(e)
        except Exception as e:
            return HttpResponse(e)
    template = loader.get_template("chat/start_chat.html")
    context = {}
    return HttpResponse(template.render(context, request))


def message(request, id):
    message = get_object_or_404(models.Message, pk=id)
    template = loader.get_template('chat/message.html')
    context = {"message": message}
    return HttpResponse(template.render(context, request))
