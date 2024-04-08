from django.shortcuts import render as django_render
from django.template import loader


def render(request, template_name, context={}, target="main", status=200):
    if request.headers.get("Transcendence"):
        response = django_render(request, template_name, context, status=status)
        response["Target"] = target
        return response

    template_html = loader.get_template(template_name).render(context, request)

    response = django_render(request, "index.html", {
        "main": template_html
    }, status=status)
    return response
