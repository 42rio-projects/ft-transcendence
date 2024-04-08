from django.shortcuts import render as django_render
from django.template.loader import render_to_string


def render(request, template_name, context={}, target="main", status=200):
    if request.headers.get("Transcendence"):
        response = django_render(request, template_name, context, status=status)
        response["Target"] = target
        return response

    response = django_render(request, "index.html", {
        "main": render_to_string(template_name, context)
    }, status=status)
    return response
