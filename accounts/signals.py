from django.db import models
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import F, Case, When
from .models import WatchlistItem
from reviews.models import Review
from movies.models import Movie
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_notification(sender, instance, created, **kwargs):
    """
    Send a welcome notification when a new user is created.
    """
    if created:
        try:
            logger.info(f"New user account created: {instance.username}")
            # from django.core.mail import send_mail
            # from django.conf import settings
            # send_mail(
            #     'Welcome to Cinema!',
            #     f'Welcome {instance.first_name or instance.username}! Start building your movie watchlist.',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [instance.email],
            #     fail_silently=True,
            # )
        except Exception as e:
            logger.error(f"Error in user creation notification: {e}")


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
