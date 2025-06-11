from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("movies/", views.movie_list, name="movie_list"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
