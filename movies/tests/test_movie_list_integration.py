from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from movies.models import Movie, Genre, Category, Country, Year

TEST_MEDIA_ROOT = "/tmp/test_media_movies"


def _poster(name="p.jpg"):
    """
    Helper to create a tiny in-memory fake image file for poster uploads.
    """
    return SimpleUploadedFile(name, b"\x47\x49\x46", content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class MovieListIntegrationTests(TestCase):
    """
    Integration tests for the movie list view verifying:
    - Page renders with all movies
    - Filtering by genre, category, country, year
    - Combined filtering logic
    """

    @classmethod
    def setUpTestData(cls):
        cls.g_action = Genre.objects.create(name="Action")
        cls.g_drama = Genre.objects.create(name="Drama")
        cls.c_film = Category.objects.create(name="Film")
        cls.c_series = Category.objects.create(name="Series")
        cls.country_usa = Country.objects.create(name="USA")
        cls.country_uk = Country.objects.create(name="UK")
        cls.y2023 = Year.objects.create(year=2023)
        cls.y2024 = Year.objects.create(year=2024)

        # Movie 1
        m1 = Movie.objects.create(
            title="Movie 1",
            description="Some description 1",
            year=cls.y2023,
            country=cls.country_usa,
            category=cls.c_film,
            duration=125,
            trailer_url="https://example.com/a",
            poster=_poster("a.jpg"),
        )
        m1.genres.add(cls.g_action)

        # Movie 2
        m2 = Movie.objects.create(
            title="Movie 2",
            description="Some description 2",
            year=cls.y2024,
            country=cls.country_uk,
            category=cls.c_series,
            duration=95,
            trailer_url="https://example.com/b",
            poster=_poster("b.jpg"),
        )
        m2.genres.add(cls.g_drama)

    def setUp(self):
        self.client = Client()

    def test_list_renders_and_shows_movies(self):
        """Unfiltered list should show all movies."""
        url = reverse("movie_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Movie 1")
        self.assertContains(resp, "Movie 2")

    def test_filter_by_genre(self):
        """Filter by genre=Action should only return Movie 1."""
        url = reverse("movie_list")
        resp = self.client.get(url, {"genre": "Action"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Movie 1")
        self.assertNotContains(resp, "Movie 2")

    def test_filter_by_category(self):
        """Filter by category=Series should only return Movie 2."""
        url = reverse("movie_list")
        resp = self.client.get(url, {"category": "Series"})
        self.assertContains(resp, "Movie 2")
        self.assertNotContains(resp, "Movie 1")

    def test_filter_by_country(self):
        """Filter by country=USA should only return Movie 1."""
        url = reverse("movie_list")
        resp = self.client.get(url, {"country": "USA"})
        self.assertContains(resp, "Movie 1")
        self.assertNotContains(resp, "Movie 2")

    def test_filter_by_year(self):
        """Filter by year=2023 should only return Movie 1."""
        url = reverse("movie_list")
        resp = self.client.get(url, {"year": "2023"})
        self.assertContains(resp, "Movie 1")
        self.assertNotContains(resp, "Movie 2")

    def test_filters_combined(self):
        """All matching filters combined should still return only Movie 1."""
        url = reverse("movie_list")
        resp = self.client.get(
            url,
            {"genre": "Action", "country": "USA", "category": "Film", "year": "2023"},
        )
        self.assertContains(resp, "Movie 1")
        self.assertNotContains(resp, "Movie 2")
