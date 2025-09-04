from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from movies.models import Movie
from .forms import ReviewForm
from django.contrib import messages
from django.db import transaction
import logging


logger = logging.getLogger(__name__)


@login_required
def submit_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    try:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    existing_review = (
                        Review.objects.select_for_update()
                        .filter(user=request.user, movie=movie)
                        .first()
                    )
                    if existing_review:
                        messages.error(
                            request,
                            "You have already submitted a review for this movie. Please delete your existing review before submitting a new one.",
                        )
                        logger.info("User attempted to submit a duplicate review")
                        return redirect("movie_detail", movie_id=movie.id)

                    Review.objects.create(
                        user=request.user,
                        movie=movie,
                        rating=form.cleaned_data["rating"],
                        review_text=form.cleaned_data["review_text"],
                    )
                    messages.success(
                        request, "Your comment has been successfully added."
                    )
                    logger.info("Review submitted successfully")
    except Exception as e:
        logger.error(f"Error submitting review: {e}")
        messages.error(request, "An error occurred while submitting your review.")

    return redirect("movie_detail", movie_id=movie.id)


@login_required
def delete_review(request, review_id):
    try:
        review = get_object_or_404(Review, id=review_id)

        if review.user != request.user:
            logger.warning("Unauthorized review deletion attempt")
            return redirect("movie_detail", movie_id=review.movie.id)

        if request.method == "POST":
            review.delete()
            messages.success(request, "Your comment has been successfully deleted.")
            logger.info("Review deleted successfully")
            return redirect("movie_detail", movie_id=review.movie.id)

    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        messages.error(request, "An error occurred while deleting your review.")

        return redirect("home")

    return redirect("movie_detail", movie_id=review.movie.id)
