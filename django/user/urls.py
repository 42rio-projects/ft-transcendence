from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from user import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('upload_avatar', views.upload_avatar, name='upload_avatar'),
    path('change_password', views.change_password, name='change_password'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('email_change/', views.email_change, name='email_change'),
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
	path(
    'generate/totp/factor/',
    views.generate_totp_factor,
    name='generate_totp_factor'
    ),
	path(
    'list/totp/factors/',
    views.list_totp_factors,
    name='list_totp_factors'
    ),
	path(
    'verify/totp/factor/',
    views.verify_totp_factor,
    name='verify_totp_factor'
    ),
	path(
    'validate/totp/token/',
    views.validate_totp_token,
    name='validate_totp_token'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
