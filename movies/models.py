from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    year = models.IntegerField(validators=[MinValueValidator(1888)])
    country = models.CharField(max_length=100, blank=False, null=False)
    duration = models.IntegerField(blank=False, null=False)
    poster = models.ImageField(upload_to="movies/", blank=False, null=False)
    trailer_url = models.URLField(blank=False, null=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=False, null=False
    )
    genres = models.ManyToManyField(Genre, related_name="movies")

    def get_duration_in_hours_and_minutes(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}min"

    def __str__(self):
        return self.title
