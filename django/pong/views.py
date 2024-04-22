from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader

from user.models import User
import pong.models as models


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
    if request.method == "GET":
        return render(request, "pong/online_game.html")


def gameInvites(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        user = get_object_or_404(
            User,
            username=name,
        )
        try:
            request.user.invite_to_game(user)  # CREATE THIS METHOD ON USER
            # add 201 response that is not rendered on the front end
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
        elif action == 'reject':
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
