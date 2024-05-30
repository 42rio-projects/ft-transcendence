from user.models import User
from django.shortcuts import redirect,  get_object_or_404
from .utils import render_component
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from . import models


def json_error(message):
    return JsonResponse(
        {"status": "error", "message": message}
    )


def json_success(message):
    return JsonResponse(
        {"status": "success", "message": message}
    )


@async_to_sync
async def send_channel_message(group, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(group, message,)


def tournament_update(pk, json):
    send_channel_message(
        f'tournament_{pk}', {"type": "tournament.update", "json": json}
    )


def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return redirect('/profile/' + username + '/')
        else:
            return render_component(request, 'search_user_form.html', 'form', {
                'error': 'User not found',
                'username': username  # So user doesn't have to re-type
            }, status=404)

    if request.method == 'GET':
        return render_component(request, 'index.html', 'content')


def pong(request):
    if request.method == 'POST':
        user_action = request.POST.get('user-action')
        invite_id = request.POST.get('invite-id')

        invite = get_object_or_404(models.GameInvite, pk=invite_id)
        if invite.receiver != request.user:
            raise PermissionDenied

        if user_action == 'accept-game':
            invite.respond(accepted=True)
            return redirect('onlineGame', game_id=invite.game.pk)
        elif user_action == 'reject-game':
            html = render_to_string('pong/game/online/canceled.html',)
            send_channel_message(
                f'game_{invite.game.pk}',
                {
                    'type': 'game.update',
                    'json': {'status': 'canceled', 'html': html}
                },
            )
            invite.respond(accepted=False)
    return render_component(request, 'pong/pong.html', 'content')


def localGame(request):
    if request.method == 'GET':
        return render_component(request, 'pong/game/local/game.html', 'content')


def onlineGame(request, game_id):
    game = get_object_or_404(models.Game, pk=game_id)
    if game.finished:
        return render_component(request, 'pong/game/online/result.html', 'content', {
            "game": game
        })
    else:
        try:
            game_invite = models.GameInvite.objects.get(game=game)
            context = {
                "player1": game_invite.sender,
                "player2": game_invite.receiver
            }
        except Exception:
            context = {"player1": game.player1, "player2": game.player2}

        return render_component(request, 'pong/game/online/game.html', 'content', context)


def localTournament(request):
    if request.method == "GET":
        return render_component(request, "pong/tournament/local/tournament.html", "content")


def tournamentMenu(request):
    context = {}
    if request.method == 'POST':
        user_action = request.POST.get('user_action')
        if 'invite' in user_action:
            invite_id = request.POST.get('invite-id')
            try:
                invite = models.TournamentInvite.objects.get(pk=invite_id)
                pk = invite.tournament.pk
            except Exception:
                context['error'] = 'Invite no longer exists'
                user_action = ''
        if user_action == 'create-tournament':
            name = request.POST.get('tournament-name')
            try:
                tournament = models.Tournament(admin=request.user, name=name)
                tournament.save()
                return redirect(
                    'onlineTournament', tournament_id=tournament.pk
                )
            except Exception:
                context['error'] = 'Tournament with this name already exists'
        elif user_action == 'accept-invite':
            invite.respond(accepted=True)
            context['success'] = 'Invite accepted'
            html = render_to_string(
                'pong/tournament/online/player.html', {'player': request.user}
            )
            tournament_update(pk, {"status": "new_player", "html": html})
            tournament_update(pk, {"status": "delete_invite", "id": invite_id})
        elif user_action == 'reject-invite':
            invite.respond(accepted=False)
            context['success'] = 'Invite rejected'
            tournament_update(pk, {"status": "delete_invite", "id": invite_id})

    return render_component(
        request, "pong/tournament/online/menu.html", "content", context
    )


def onlineTournament(request, tournament_id):
    tournament = get_object_or_404(models.Tournament, pk=tournament_id)
    return render_component(request, "pong/tournament/online/tournament.html", "content", {"tournament": tournament})


def cancelTournament(request, tournament_id):
    try:
        tournament = models.Tournament.objects.get(pk=tournament_id)
    except Exception:
        return json_error("Tournament does not exist.")
    if request.user != tournament.admin:
        return json_error("You're not tournament admin.")
    try:
        pk = tournament.pk
        tournament.cancel()
        html = render_to_string('pong/tournament/online/cancelled.html')
        tournament_update(pk, {"status": "cancelled", "html": html})
        return json_success(f"Tournament {tournament.name} cancelled.")
    except Exception as e:
        return json_error(e.__str__())


def inviteToTournament(request, tournament_id):
    if request.method != 'POST':
        return redirect('pongMenu')
    try:
        tournament = models.Tournament.objects.get(pk=tournament_id)
    except Exception:
        return json_error("Tournament does not exist.")
    try:
        name = request.POST.get('username')
        user = User.objects.get(username=name)
    except Exception:
        return json_error(f"User '{name}' does not exist.")
    try:
        if request.user != tournament.admin:
            raise Exception("You're not tournament admin.")
        invite = tournament.invite(user)
        html = render_to_string(
            'pong/tournament/online/invite_sent.html', {'invite': invite}
        )
        tournament_update(
            tournament.pk, {"status": "new_invite", "html": html}
        )
        return json_success(f"Invite sent to {name}")
    except Exception as e:
        return json_error(e.__str__())
