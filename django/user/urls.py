from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from user import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),

    path('profile/', views.my_profile),
    path('profile/<str:username>', views.user_profile),

    path('upload_avatar', views.upload_avatar),
    path('change_password', views.change_password),
    path('email_change/', views.email_change),
    path(
        'email_verify_code/',
        views.email_verify_code,
        name='email_verify_code'
    ),
    path(
        'email_verify_check/',
        views.email_verify_check,
        name='email_verify_check'
    ),
    path(
        'email_change_check/',
        views.email_change_check,
        name='email_change_check'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
