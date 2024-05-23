from django.shortcuts import render
from django.template import loader


def render_component(request, template_name, target, context={}, status=200):
    if request.headers.get('X-Transcendence'):
        response = render(request, template_name, context, status=status)
        response['X-Target-Id'] = target
        return response

    component_html = loader.get_template(template_name).render(context, request)
    return render(request, 'base.html', { 'content': component_html }, status=status)
