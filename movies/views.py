from django.shortcuts import render, get_object_or_404
from .models import Movie, Genre, Category


def movie_list(request):
    genre_id = request.GET.get("genre")
    category_id = request.GET.get("category")

    movies = Movie.objects.all()

    if genre_id:
        movies = movies.filter(genres__id=genre_id)

    if category_id:
        movies = movies.filter(category__id=category_id)

    movies = movies.distinct()

    genres = Genre.objects.all()
    categories = Category.objects.all()

    return render(
        request,
        "movies/movie_list.html",
        {"movies": movies, "genres": genres, "categories": categories},
    )


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movies/movie_detail.html", {"movie": movie})
