import pong.models as models
from user.models import User
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from django.shortcuts import render
from asgiref.sync import async_to_sync


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
        return redirect('gameInvites')
    return render(request, "pong/online_game.html")


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
                {"type": "game.update", "json": {"status": "canceled"}},
            )
            invite.respond(accepted=False)
        else:
            raise Exception('Invalid action')
    return redirect('gameInvites')


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
