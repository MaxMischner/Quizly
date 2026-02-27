"""
URL Routing für User-Management.
"""
from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    # Authentifizierung
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
