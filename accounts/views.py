from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from movies.models import Movie
from .models import WatchlistItem
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)

                return redirect("home")

            except Exception as e:
                logger.error(f"Error during signup: {e}")
                messages.error(request, "An error occurred during registration.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        with transaction.atomic():
            watchlist_item, created = WatchlistItem.objects.select_for_update().get_or_create(
                user=request.user,
                movie=movie
            )

            if created:
                messages.success(request, f"{movie.title} has been added to your watchlist.")
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
            watchlist_item = WatchlistItem.objects.select_for_update().filter(
                user=request.user, movie=movie
            ).first()

            if watchlist_item:
                watchlist_item.delete()
                messages.success(request, f"{movie.title} has been removed from your watchlist.")
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
        request, "accounts/watchlist.html", {"watchlist_items": watchlist_items}
    )
