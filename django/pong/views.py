from user.models import User
from django.shortcuts import get_object_or_404, redirect
from .utils import render_component

# Create your views here.


def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = get_object_or_404(User, username=username)
        except:
            return render_component(request, 'search_user_form.html', 'form', {
                'error': 'User not found',
                'username': username # So user doesn't have to re-type
            }, status=404)

        return redirect('/profile/' + user.username + '/')

    return render_component(request, 'index.html', 'content')
