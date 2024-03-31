from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from user.models import User
import chat.models as models


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
    if chat.starter != request.user and chat.receiver != request.user:
        return HttpResponseForbidden('Not your chat')
    other_user = chat.receiver if chat.starter == request.user else chat.starter
    if other_user in request.user.get_blocks():
        return HttpResponseForbidden('This user was blocked')
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
    template = loader.get_template('chat/chat.html')
    context = {"chat": chat}
    return HttpResponse(template.render(context, request))


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
