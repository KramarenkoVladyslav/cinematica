from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.name


class MovieManager(models.Manager):
    def filter_by_genre(self, queryset, genre_id):
        try:
            return queryset.filter(genres__id=int(genre_id))
        except (ValueError, TypeError):
            return queryset

    def filter_by_category(self, queryset, category_id):
        try:
            return queryset.filter(category__id=int(category_id))
        except (ValueError, TypeError):
            return queryset

    def filter_by_country(self, queryset, country):
        try:
            return queryset.filter(country=country)
        except (ValueError, TypeError):
            return queryset

    def filter_by_year(self, queryset, year):
        try:
            return queryset.filter(year=int(year))
        except (ValueError, TypeError):
            return queryset

    def apply_all_filters(
        self, genre_id=None, category_id=None, country=None, year=None
    ):
        queryset = (
            self.get_queryset().select_related("category").prefetch_related("genres")
        )
        if genre_id:
            queryset = self.filter_by_genre(queryset, genre_id)
        if category_id:
            queryset = self.filter_by_category(queryset, category_id)
        if country:
            queryset = self.filter_by_country(queryset, country)
        if year:
            queryset = self.filter_by_year(queryset, year)
        return queryset.distinct()


class Movie(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    year = models.IntegerField(validators=[MinValueValidator(1888)])
    country = models.CharField(max_length=100, blank=False, null=False)
    duration = models.IntegerField(blank=False, null=False)
    poster = models.ImageField(upload_to="movies/", blank=False, null=False)
    trailer_url = models.URLField(blank=False, null=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True
    )
    genres = models.ManyToManyField(Genre, related_name="movies")

    objects = MovieManager()

    def get_duration_in_hours_and_minutes(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}min"

    def __str__(self):
        return self.title
