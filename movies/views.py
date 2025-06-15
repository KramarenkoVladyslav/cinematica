from django.shortcuts import render, get_object_or_404
from .models import Movie, Genre, Category
from reviews.models import Review
from reviews.forms import ReviewForm
from accounts.models import WatchlistItem


def filter_movies_by_genre(movies, genre_id):
    try:
        genre_id = int(genre_id)
        return movies.filter(genres__id=genre_id)
    except (ValueError, TypeError):
        return movies


def filter_movies_by_category(movies, category_id):
    try:
        category_id = int(category_id)
        return movies.filter(category__id=category_id)
    except (ValueError, TypeError):
        return movies


def filter_movies_by_country(movies, country):
    try:
        return movies.filter(country=country)
    except (ValueError, TypeError):
        return movies


def filter_movies_by_year(movies, year):
    try:
        year = int(year)
        return movies.filter(year=year)
    except (ValueError, TypeError):
        return movies


def movie_list(request):
    genre_id = request.GET.get("genre")
    category_id = request.GET.get("category")
    country = request.GET.get("country")
    year = request.GET.get("year")

    movies = Movie.objects.all().select_related("category").prefetch_related("genres")

    if genre_id:
        movies = filter_movies_by_genre(movies, genre_id)

    if category_id:
        movies = filter_movies_by_category(movies, category_id)

    if country:
        movies = filter_movies_by_country(movies, country)

    if year:
        movies = filter_movies_by_year(movies, year)

    movies = movies.distinct()

    genres = Genre.objects.all()
    categories = Category.objects.all()
    years = Movie.objects.values_list("year", flat=True).distinct()
    countries = Movie.objects.values_list("country", flat=True).distinct()

    return render(
        request,
        "movies/movie_list.html",
        {
            "movies": movies,
            "genres": genres,
            "categories": categories,
            "years": years,
            "countries": countries,
        },
    )


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = (
        Review.objects.filter(movie=movie)
        .select_related("user")
        .order_by("-created_at")
    )
    form = ReviewForm()
    watchlist_items = WatchlistItem.objects.filter(user=request.user).values_list(
        "movie_id", flat=True
    )

    return render(
        request,
        "movies/movie_detail.html",
        {
            "movie": movie,
            "reviews": reviews,
            "watchlist_items": watchlist_items,
            "form": form,
        },
    )
