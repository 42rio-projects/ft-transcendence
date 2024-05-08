from .utils import render_component

# Create your views here.


def home(request):
    if request.method == "GET":
        return render_component(request, "home.html", "content")
