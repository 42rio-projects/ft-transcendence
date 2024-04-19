from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import loader

from user.models import User


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


def onlineGame(request):
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
