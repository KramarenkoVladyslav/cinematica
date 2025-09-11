from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
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
