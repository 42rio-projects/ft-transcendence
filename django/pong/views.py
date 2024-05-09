import pong.models as models
from user.models import User
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from django.shortcuts import render
from asgiref.sync import async_to_sync
from django.http import HttpResponseForbidden


@async_to_sync
async def send_channel_message(group, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group,
        message,
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
        return render(request, "pong/local_game.html")


def onlineGame(request, game_id):
    game = get_object_or_404(models.Game, pk=game_id)
    if game.finished:
        template = loader.get_template('pong/game_result.html')
        context = {"game": game}
    else:
        template = loader.get_template('pong/online_game.html')
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
    template = loader.get_template("pong/game_invites.html")
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
        return render(request, "pong/local_tournament.html")


def tournamentInvites(request):
    if request.method == 'POST':
        name = request.POST.get('tournament-name')
        try:
            tournament = models.Tournament(admin=request.user, name=name)
            tournament.save()
            return redirect('onlineTournament', tournament_id=tournament.pk)
        except Exception as e:
            # add 40x response that is not rendered on the front end
            return HttpResponse(e)
    template = loader.get_template("pong/tournament_invites.html")
    context = {}
    return HttpResponse(template.render(context, request))


def onlineTournament(request, tournament_id):
    tournament = get_object_or_404(models.Tournament, pk=tournament_id)
    if request.method == 'POST':
        if request.user != tournament.admin:
            return HttpResponseForbidden("You're not tournament admin.")
        if tournament.started:
            return HttpResponseForbidden("Tournament already started")
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            tournament.invite(user)
        except Exception as e:
            return HttpResponse(e)
    context = {"tournament": tournament}
    if tournament.finished:
        template = loader.get_template('pong/online_tournament_result.html')
    else:
        template = loader.get_template('pong/online_tournament.html')
    return HttpResponse(template.render(context, request))


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
            invite.respond(accepted=True)
        elif action == 'reject':
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
    return redirect('tournamentInvites')

# class TournamentViewSet(viewsets.ModelViewSet):
#     queryset = models.Tournament.objects.all()
#     lookup_field = 'name'
#     serializer_class = serializers.TournamentSerializer
#     permission_classes = [IsAuthenticated]
#
#     # temporary API endpoint to advance tournament
#     @action(detail=True, methods=['GET'])
#     def advance(self, request, name=None):
#         tournament = self.get_object()
#         tournament.new_round()
#         return Response({'status': 'tournament round advanced'})
