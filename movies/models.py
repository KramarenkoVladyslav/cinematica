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


class Country(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    code = models.CharField(
        max_length=3, blank=True, null=True, unique=True
    )  # ISO country code

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Year(models.Model):
    year = models.IntegerField(validators=[MinValueValidator(1888)], unique=True)

    def __str__(self):
        return str(self.year)


class MovieManager(models.Manager):
    @staticmethod
    def filter_by_genre(queryset, genre_name):
        if genre_name:
            return queryset.filter(genres__name__iexact=genre_name)
        return queryset

    @staticmethod
    def filter_by_category(queryset, category_name):
        if category_name:
            return queryset.filter(category__name__iexact=category_name)
        return queryset

    @staticmethod
    def filter_by_country(queryset, country_name):
        if country_name:
            return queryset.filter(country__name__iexact=country_name)
        return queryset

    @staticmethod
    def filter_by_year(queryset, year_value):
        if year_value:
            try:
                year_int = int(year_value)
                return queryset.filter(year__year=year_int)
            except (ValueError, TypeError):
                return queryset
        return queryset

    def apply_all_filters(
        self, genre_name=None, category_name=None, country_name=None, year=None
    ):
        queryset = (
            self.get_queryset()
            .select_related("category", "country", "year")
            .prefetch_related("genres")
        )
        if genre_name:
            queryset = self.filter_by_genre(queryset, genre_name)
        if category_name:
            queryset = self.filter_by_category(queryset, category_name)
        if country_name:
            queryset = self.filter_by_country(queryset, country_name)
        if year:
            queryset = self.filter_by_year(queryset, year)
        return queryset.distinct()


class Movie(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, blank=False, null=False)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=False, null=False
    )
    duration = models.IntegerField(blank=False, null=False)
    poster = models.ImageField(upload_to="movies/", blank=False, null=False)
    trailer_url = models.URLField(blank=False, null=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True
    )
    genres = models.ManyToManyField(Genre, related_name="movies")

    watchlist_count = models.PositiveIntegerField(default=0)
    review_count = models.PositiveIntegerField(default=0)

    objects = MovieManager()

    def get_duration_in_hours_and_minutes(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}min"

    def __str__(self):
        return self.title
