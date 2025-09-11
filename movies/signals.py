from django.db.models.signals import post_delete, post_save, pre_delete
from django.db.models import F, Case, When
from django.db import models
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import Movie, WatchlistItem
from reviews.models import Review
import logging

User = get_user_model()
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


@receiver(post_save, sender=WatchlistItem)
def watchlist_item_added(sender, instance, created, **kwargs):
    """
    Log watchlist additions and update movie watchlist count.
    """
    if created:
        try:
            logger.info(
                f"User {instance.user.username} added movie '{instance.movie.title}' to watchlist"
            )

            # Atomically increment the movie's watchlist count
            Movie.objects.filter(id=instance.movie.id).update(
                watchlist_count=F("watchlist_count") + 1
            )

        except Exception as e:
            logger.error(f"Error logging watchlist addition: {e}")


@receiver(post_delete, sender=WatchlistItem)
def watchlist_item_removed(sender, instance, **kwargs):
    """
    Log watchlist removals and update movie watchlist count.
    """
    try:
        logger.info(
            f"User {instance.user.username} removed movie '{instance.movie.title}' from watchlist"
        )

        Movie.objects.filter(id=instance.movie.id).update(
            watchlist_count=Case(
                When(watchlist_count__gt=0, then=F("watchlist_count") - 1),
                default=0,
                output_field=models.PositiveIntegerField(),
            )
        )

    except Exception as e:
        logger.error(f"Error logging watchlist removal: {e}")


@receiver(pre_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up user-related data before user deletion.
    """
    try:
        watchlist_count = WatchlistItem.objects.filter(user=instance).count()
        review_count = Review.objects.filter(user=instance).count()

        logger.info(
            f"Preparing to delete user {instance.username}: "
            f"{watchlist_count} watchlist items, {review_count} reviews"
        )

    except Exception as e:
        logger.error(f"Error in user cleanup preparation: {e}")
