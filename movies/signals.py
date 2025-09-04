import os
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Movie
from accounts.models import WatchlistItem
from reviews.models import Review
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Movie)
def movie_saved(sender, instance, created, **kwargs):
    """
    Handle movie creation and updates.
    """
    try:
        if created:
            logger.info(
                f"New movie added to catalog: '{instance.title}' ({instance.year})"
            )
        else:
            logger.info(f"Movie updated: '{instance.title}' ({instance.year})")

        cache_key = f"movie_stats_{instance.id}"
        cache.delete(cache_key)

        cache.delete("movie_list_cache")

    except Exception as e:
        logger.error(f"Error in movie save signal: {e}")


@receiver(pre_delete, sender=Movie)
def cleanup_movie_relations(sender, instance, **kwargs):
    """
    Clean up related data before movie deletion.
    """
    try:
        watchlist_count = WatchlistItem.objects.filter(movie=instance).count()
        review_count = Review.objects.filter(movie=instance).count()

        logger.warning(
            f"Preparing to delete movie '{instance.title}': "
            f"{watchlist_count} watchlist entries, {review_count} reviews will be removed"
        )

        cache_key = f"movie_stats_{instance.id}"
        cache.delete(cache_key)

    except Exception as e:
        logger.error(f"Error in movie cleanup signal: {e}")
