from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from movies.models import Movie
from .forms import ReviewForm
from django.contrib import messages


@login_required
def submit_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    existing_review = Review.objects.filter(user=request.user, movie=movie).first()
    if existing_review:
        messages.error(
            request,
            "You have already submitted a review for this movie. Please delete your existing review before submitting a new one.",
        )
        return redirect("movie_detail", movie_id=movie.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                user=request.user,
                movie=movie,
                rating=form.cleaned_data["rating"],
                review_text=form.cleaned_data["review_text"],
            )
    return redirect("movie_detail", movie_id=movie.id)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return redirect("movie_detail", movie_id=review.movie.id)

    if request.method == "POST":
        review.delete()

    return redirect("movie_detail", movie_id=review.movie.id)
