from django.shortcuts import render, get_object_or_404
from .models import Movie, Genre, Category, Country, Year
from reviews.models import Review
from reviews.forms import ReviewForm
from accounts.models import WatchlistItem


def movie_list(request):
    genre_id = request.GET.get("genre")
    category_id = request.GET.get("category")
    country = request.GET.get("country")
    year = request.GET.get("year")

    movies = Movie.objects.apply_all_filters(
        genre_id=genre_id, category_id=category_id, country=country, year=year
    )

    genres = Genre.objects.all()
    categories = Category.objects.all()
    years = Year.objects.all().order_by('-year')
    countries = Country.objects.all().order_by('name')

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