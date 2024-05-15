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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # For avatar images
