from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from movies.models import Movie, Category, Genre, Country, Year

TEST_MEDIA_ROOT = "/tmp/test_media_movies_model"


def _poster(name="p.jpg"):
    return SimpleUploadedFile(name, b"\x47\x49\x46", content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class MovieModelTests(TestCase):
    def test_movie_creation_success(self):
        category = Category.objects.create(name="Action")
        genre1 = Genre.objects.create(name="Thriller")
        genre2 = Genre.objects.create(name="Adventure")
        year = Year.objects.create(year=2024)
        country = Country.objects.create(name="USA")

        movie = Movie.objects.create(
            title="Test Movie",
            description="Some description",
            year=year,
            country=country,
            duration=125,
            poster=_poster(),
            trailer_url="https://example.com/trailer",
            category=category,
        )
        movie.genres.set([genre1, genre2])

        self.assertEqual(Movie.objects.count(), 1)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.category, category)
        self.assertEqual(movie.year, year)
        self.assertEqual(movie.country, country)
        self.assertSetEqual(set(movie.genres.all()), {genre1, genre2})
        self.assertEqual(movie.get_duration_in_hours_and_minutes(), "2h 5min")

    def test_duration_formatting_exact_hours(self):
        year = Year.objects.create(year=2000)
        country = Country.objects.create(name="UK")
        movie = Movie.objects.create(
            title="Exact Hours",
            description="Desc",
            year=year,
            country=country,
            duration=120,
            poster=_poster("exact.jpg"),
            trailer_url="https://example.com",
        )
        self.assertEqual(movie.get_duration_in_hours_and_minutes(), "2h 0min")

    def test_str_returns_title(self):
        year = Year.objects.create(year=1999)
        country = Country.objects.create(name="France")
        movie = Movie.objects.create(
            title="My Film",
            description="Desc",
            year=year,
            country=country,
            duration=90,
            poster=_poster("str.jpg"),
            trailer_url="https://example.com",
        )
        self.assertEqual(str(movie), "My Film")
