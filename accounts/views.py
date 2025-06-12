from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from movies.models import Movie
from .models import WatchlistItem


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "POST":
        try:
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect("home")
        except Exception as e:
            print(e)

    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    WatchlistItem.objects.get_or_create(user=request.user, movie=movie)
    return redirect("watchlist")


@login_required
def remove_from_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    WatchlistItem.objects.filter(user=request.user, movie=movie).delete()
    return redirect("watchlist")


@login_required
def watchlist(request):
    watchlist_items = WatchlistItem.objects.filter(user=request.user).select_related(
        "movie"
    )
    return render(
        request, "accounts/watchlist.html", {"watchlist_items": watchlist_items}
    )
