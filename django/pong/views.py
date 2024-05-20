from user.models import User
from django.shortcuts import redirect
from .utils import render_component
from asgiref.sync import async_to_sync

# Create your views here.


def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return redirect('/profile/' + username + '/')
        else:
            return render_component(request, 'search_user_form.html', 'form', {
                'error': 'User not found',
                'username': username # So user doesn't have to re-type
            }, status=404)

    if request.method == 'GET':
        return render_component(request, 'index.html', 'content')

def main(request):
    if request.method == 'GET':
        return render_component(request, 'pong/main.html', 'content')


def gameMenu(request):
    if request.method == 'GET':
        return render_component(request, 'pong/game_menu.html', 'content')


def localGame(request):
    if request.method == 'GET':
        return render_component(request, 'pong/local_game.html', 'content')


def onlineGame(request, game_id):
    if request.method == 'GET':
        return render_component(request, 'pong/online_game.html', 'content')


def gameInvites(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            game = request.user.invite_to_game(user)
            return redirect('onlineGame', game_id=game.pk)
        except Exception as e:
            # add 40x response that is not rendered on the front end
            return HttpResponse(e)
    template = loader.get_template('pong/game_invites.html')
    context = {}
    return HttpResponse(template.render_component(context, request))


@async_to_sync
async def send_channel_message(group, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group,
        message,
    )


def respondGameInvite(request, invite_id):
    invite = get_object_or_404(
        models.GameInvite,
        pk=invite_id,
    )
    if invite.receiver != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            invite.respond(accepted=True)
            return redirect('onlineGame', game_id=invite.game.pk)
        elif action == 'reject':
            invite.game.pk
            send_channel_message(
                f'game_{invite.game.pk}',
                {'type': 'game.update', 'json': {'status': 'canceled'}},
            )
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
    return redirect('gameInvites')
