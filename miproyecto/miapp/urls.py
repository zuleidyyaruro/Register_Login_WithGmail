from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.profile_View.as_view(), name='profile'),
    path('accounts/', include('allauth.urls')),
    path('', TemplateView.as_view(template_name="index.html",)), 
    path('confirm-email/<str:user_id>/<str:token>/', views.ConfirmRegistrationView.as_view(), name='confirm_email'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
