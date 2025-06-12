from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Watchlist
    path("watchlist/", views.watchlist, name="watchlist"),
    path(
        "add_to_watchlist/<int:movie_id>/",
        views.add_to_watchlist,
        name="add_to_watchlist",
    ),
    path(
        "remove_from_watchlist/<int:movie_id>/",
        views.remove_from_watchlist,
        name="remove_from_watchlist",
    ),
]
