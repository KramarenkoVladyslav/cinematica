from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db.models import F, Case, When
from .models import Review
from movies.models import Movie
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def review_saved(sender, instance, created, **kwargs):
    """
    Handle review creation and updates, maintaining review count.
    Essential for maintaining movie analytics and user engagement in a cinema platform.
    """
    try:
        if created:
            logger.info(
                f"New review created: User {instance.user.username} "
                f"rated '{instance.movie.title}' {instance.rating}/5"
            )

            # Atomically increment the movie's review count
            Movie.objects.filter(id=instance.movie.id).update(
                review_count=F("review_count") + 1
            )

        else:
            logger.info(
                f"Review updated: User {instance.user.username} "
                f"updated review for '{instance.movie.title}'"
            )

        # Clear cached movie statistics when review data changes
        cache_key = f"movie_stats_{instance.movie.id}"
        cache.delete(cache_key)

    except Exception as e:
        logger.error(f"Error in review save signal: {e}")


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    """
    Handle review deletion cleanup and update review count.
    """
    try:
        logger.info(
            f"Review deleted: User {instance.user.username} "
            f"removed review for '{instance.movie.title}'"
        )

        # Atomically decrement the movie's review count with a minimum of 0
        Movie.objects.filter(id=instance.movie.id).update(
            review_count=Case(
                When(review_count__gt=0, then=F("review_count") - 1),
                default=0,
                output_field=models.PositiveIntegerField(),
            )
        )

        # Clear cached movie statistics
        cache_key = f"movie_stats_{instance.movie.id}"
        cache.delete(cache_key)

    except Exception as e:
        logger.error(f"Error in review deletion signal: {e}")


@receiver(pre_save, sender=Review)
def validate_review_integrity(sender, instance, **kwargs):
    """
    Validate review data integrity before saving.
    """
    try:
        if instance.rating < 1 or instance.rating > 5:
            logger.warning(
                f"Invalid rating attempt: User {instance.user.username} "
                f"attempted rating {instance.rating} for '{instance.movie.title}'"
            )

        if instance.review_text and len(instance.review_text) > 1000:
            logger.info(
                f"Long review submitted: {len(instance.review_text)} characters "
                f"by {instance.user.username} for '{instance.movie.title}'"
            )

    except Exception as e:
        logger.error(f"Error in review validation signal: {e}")
