from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Genre, Category, Country, Year, WatchlistItem
from reviews.models import Review
from reviews.forms import ReviewForm

logger = logging.getLogger(__name__)


def movie_list(request):
    genre = request.GET.get("genre")
    category = request.GET.get("category")
    country = request.GET.get("country")
    year = request.GET.get("year")

    movies = Movie.objects.apply_all_filters(
        genre_name=genre, category_name=category, country_name=country, year=year
    )

    genres = Genre.objects.all()
    categories = Category.objects.all()
    years = Year.objects.all().order_by("-year")
    countries = Country.objects.all().order_by("name")

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
    if request.user.is_authenticated:
        watchlist_items = WatchlistItem.objects.filter(user=request.user).values_list(
            "movie_id", flat=True
        )
    else:
        watchlist_items = []

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


@login_required
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        with transaction.atomic():
            (
                watchlist_item,
                created,
            ) = WatchlistItem.objects.select_for_update().get_or_create(
                user=request.user, movie=movie
            )

            if created:
                messages.success(
                    request, f"{movie.title} has been added to your watchlist."
                )
                logger.info("User successfully added to watchlist")
            else:
                messages.info(request, f"{movie.title} is already in your watchlist.")

    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        messages.error(request, "An error occurred while adding to your watchlist.")

    return redirect("movie_detail", movie_id=movie.id)


@login_required
def remove_from_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        with transaction.atomic():
            watchlist_item = (
                WatchlistItem.objects.select_for_update()
                .filter(user=request.user, movie=movie)
                .first()
            )

            if watchlist_item:
                watchlist_item.delete()
                messages.success(
                    request, f"{movie.title} has been removed from your watchlist."
                )
                logger.info("User successfully removed from watchlist")
            else:
                messages.info(request, f"{movie.title} was not in your watchlist.")

    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        messages.error(request, "An error occurred while removing from your watchlist.")

    next_url = request.POST.get("next", "watchlist")
    return redirect(next_url)


@login_required
def watchlist(request):
    try:
        watchlist_items = WatchlistItem.objects.filter(
            user=request.user
        ).select_related("movie")
        logger.info("Watchlist accessed successfully")
    except Exception as e:
        logger.error(f"Error accessing watchlist: {e}")
        messages.error(request, "An error occurred while accessing your watchlist.")
        watchlist_items = []
    return render(
        request, "movies/watchlist.html", {"watchlist_items": watchlist_items}
    )
