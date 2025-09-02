import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Movie


@receiver(post_delete, sender=Movie)
def delete_movie_poster(sender, instance, **kwargs):
    """
    Delete the poster file from the filesystem when a Movie instance is deleted.
    """
    if instance.poster:
        if os.path.isfile(instance.poster.path):
            os.remove(instance.poster.path)
