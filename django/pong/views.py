import pong.models as models
from user.models import User
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from django.shortcuts import render
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.template.loader import render_to_string


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
    if request.method == "GET":
        return render(request, "pong/index.html")


def main(request):
    if request.method == "GET":
        return render(request, "pong/main.html")


def gameMenu(request):
    if request.method == "GET":
        return render(request, "pong/game_menu.html")


def localGame(request):
    if request.method == "GET":
        return render(request, "pong/game/local/game.html")


def onlineGame(request, game_id):
    game = get_object_or_404(models.Game, pk=game_id)
    if game.finished:
        template = loader.get_template('pong/game/online/result.html')
        context = {"game": game}
    else:
        template = loader.get_template('pong/game/online/game.html')
        try:
            game_invite = models.GameInvite.objects.get(game=game)
            context = {
                "player1": game_invite.sender,
                "player2": game_invite.receiver
            }
        except Exception:
            context = {"player1": game.player1, "player2": game.player2}
    return HttpResponse(template.render(context, request))


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
    template = loader.get_template("pong/game/online/invites.html")
    context = {}
    return HttpResponse(template.render(context, request))


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
            send_channel_message(
                f'game_{invite.game.pk}',
                {"type": "game.update", "json": {"status": "canceled"}},
            )
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
    return redirect('gameInvites')


def tournamentMenu(request):
    if request.method == "GET":
        return render(request, "pong/tournament_menu.html")


def localTournament(request):
    if request.method == "GET":
        return render(request, "pong/tournament/local/tournament.html")


def tournamentInvites(request):
    template = loader.get_template("pong/tournament/online/invites.html")
    context = {}
    return HttpResponse(template.render(context, request))


def createTournament(request):
    if request.method != 'POST':
        return
    name = request.POST.get('tournament-name')
    try:
        tournament = models.Tournament(admin=request.user, name=name)
        tournament.save()
        return redirect('onlineTournament', tournament_id=tournament.pk)
    except Exception as e:
        # add 40x response that is not rendered on the front end
        return HttpResponse(e)


def onlineTournament(request, tournament_id):
    if request.method != 'GET':
        return
    tournament = get_object_or_404(models.Tournament, pk=tournament_id)
    context = {"tournament": tournament}
    template = loader.get_template('pong/tournament/online/tournament.html')
    return HttpResponse(template.render(context, request))


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
        return
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


def respondTournamentInvite(request, invite_id):
    invite = get_object_or_404(
        models.TournamentInvite,
        pk=invite_id,
    )
    if invite.receiver != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            pk = invite.tournament.pk
            invite.respond(accepted=True)
            html = render_to_string(
                'pong/tournament/online/player.html', {'player': request.user}
            )
            tournament_update(pk, {"status": "new_player", "html": html})
        elif action == 'reject':
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
        tournament_update(pk, {"status": "delete_invite", "id": invite_id})
    return redirect('tournamentInvites')
