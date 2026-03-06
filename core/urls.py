"""Root URL configuration for the Quizly backend API."""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

from users.api.views import LoginView, LogoutView, RegisterView, TokenRefreshView, UserProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="profile"),
    path("api/quizzes/", include("quizzes.api.urls")),
    path("api-auth/", include("rest_framework.urls")),
]

