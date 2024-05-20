from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from user import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),

    path('profile/', views.my_profile),
    path('profile/<str:username>/', views.user_profile),
    path('edit_profile/', views.edit_profile),

    path('change_password/', views.change_password),
    path('verify_email/', views.verify_email),

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # For avatar images
