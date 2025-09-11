from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("movies/", views.movie_list, name="movie_list"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
