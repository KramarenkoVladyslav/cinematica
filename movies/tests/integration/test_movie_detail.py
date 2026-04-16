from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from movies.models import Movie, Genre, Category, Country, Year, WatchlistItem
from reviews.models import Review

User = get_user_model()
TEST_MEDIA_ROOT = "/tmp/test_media_movies"


def _poster(name="p.jpg"):
    return SimpleUploadedFile(name, b"\x47\x49\x46", content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class MovieDetailIntegrationTests(TestCase):
    """Integration tests for the movie detail view.

    Verifies:
    - Rendering and template usage for anonymous and authenticated users
    - Display of movie metadata (title, description, duration formatting, genres, country, year, trailer link)
    - Review retrieval, presence, and ordering
    - Watchlist button state logic across different user scenarios
    - Behavior when a movie has no reviews
    - 404 handling for non-existent movie IDs
    - Edge cases for duration formatting
    """

    @classmethod
    def setUpTestData(cls):
        cls.genre1 = Genre.objects.create(name="Action")
        cls.genre2 = Genre.objects.create(name="Drama")
        cls.category = Category.objects.create(name="Film")
        cls.country = Country.objects.create(name="USA", code="US")
        cls.year = Year.objects.create(year=2023)

        cls.movie = Movie.objects.create(
            title="Test Movie Title",
            description="A detailed description of the test movie for verification purposes.",
            year=cls.year,
            country=cls.country,
            category=cls.category,
            duration=135,
            trailer_url="https://example.com/trailer",
            poster=_poster("test_movie.jpg"),
        )
        cls.movie.genres.add(cls.genre1, cls.genre2)

        cls.user = User.objects.create_user(username="john", password="pwd12345")
        cls.other_user = User.objects.create_user(username="maria", password="pwd12345")
        cls.third_user = User.objects.create_user(username="vlad", password="pwd12345")

        cls.review1 = Review.objects.create(
            movie=cls.movie,
            user=cls.user,
            review_text="Great movie with excellent action scenes!",
            rating=5,
        )
        cls.review2 = Review.objects.create(
            movie=cls.movie,
            user=cls.other_user,
            review_text="Ok movie, but could be better",
            rating=3,
        )

        WatchlistItem.objects.create(user=cls.user, movie=cls.movie)

        cls.movie2 = Movie.objects.create(
            title="Another Movie",
            description="Another movie description",
            year=cls.year,
            country=cls.country,
            category=cls.category,
            duration=90,
            trailer_url="https://example.com/trailer2",
            poster=_poster("another_movie.jpg"),
        )

    def setUp(self):
        self.client = Client()

    def test_movie_detail_renders_for_anonymous_user(self):
        """Test that movie detail page renders correctly for anonymous users"""
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "movies/movie_detail.html")
        self.assertContains(resp, self.movie.title)
        self.assertContains(resp, self.movie.description)
        self.assertContains(resp, "2h 15min")
        self.assertContains(resp, self.country.name)
        self.assertContains(resp, str(self.year.year))
        self.assertContains(resp, self.genre1.name)
        self.assertContains(resp, self.genre2.name)
        self.assertContains(resp, f'href="{self.movie.trailer_url}"')
        self.assertContains(resp, "Add to Watchlist")
        self.assertNotContains(resp, "In Watchlist")

    def test_movie_detail_contains_all_reviews(self):
        """Test that all reviews are displayed with correct data"""
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, self.review1.review_text)
        self.assertContains(resp, self.review2.review_text)
        self.assertContains(resp, self.user.username)
        self.assertContains(resp, self.other_user.username)

    def test_movie_detail_context_data(self):
        """Test that the view passes correct context data to template"""
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertEqual(resp.context["movie"], self.movie)
        self.assertIn("reviews", resp.context)
        self.assertIn("form", resp.context)
        self.assertIn("watchlist_items", resp.context)
        self.assertGreaterEqual(len(resp.context["reviews"]), 2)

    def test_watchlist_button_for_user_with_item_in_watchlist(self):
        """Test that users with movie in watchlist see 'Remove' button"""
        self.client.login(username="john", password="pwd12345")
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, "In Watchlist")
        self.assertNotContains(resp, "Add to Watchlist")
        self.assertIn(self.movie.id, resp.context["watchlist_items"])

    def test_watchlist_button_for_user_without_item_in_watchlist(self):
        """Test that users without movie in watchlist see 'Add' button"""
        self.client.login(username="vlad", password="pwd12345")
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, "Add to Watchlist")
        self.assertNotContains(resp, "In Watchlist")
        self.assertNotIn(self.movie.id, resp.context["watchlist_items"])

    def test_movie_detail_with_different_user_watchlist(self):
        """Test watchlist functionality for user with different movies in watchlist"""
        WatchlistItem.objects.create(user=self.third_user, movie=self.movie2)
        self.client.login(username="vlad", password="pwd12345")
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, "Add to Watchlist")
        self.assertIn(self.movie2.id, resp.context["watchlist_items"])
        self.assertNotIn(self.movie.id, resp.context["watchlist_items"])

    def test_movie_detail_nonexistent_movie_returns_404(self):
        """Test that requesting non-existent movie returns 404"""
        url = reverse("movie_detail", args=[99999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_movie_detail_with_no_reviews(self):
        """Test movie detail page when movie has no reviews"""
        url = reverse("movie_detail", args=[self.movie2.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.movie2.title)
        self.assertEqual(len(resp.context["reviews"]), 0)

    def test_movie_detail_form_present_for_authenticated_user(self):
        """Test that review form is present for authenticated users"""
        self.client.login(username="maria", password="pwd12345")
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertIn("form", resp.context)
        self.assertIsNotNone(resp.context["form"])

    def test_movie_detail_displays_all_genres(self):
        """Test that all movie genres are displayed"""
        url = reverse("movie_detail", args=[self.movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, "Action")
        self.assertContains(resp, "Drama")

    def test_movie_with_single_digit_duration_formatting(self):
        """Test duration formatting for movies with different durations"""
        short_movie = Movie.objects.create(
            title="Short Movie",
            description="A short movie",
            year=self.year,
            country=self.country,
            category=self.category,
            duration=90,
            trailer_url="https://example.com/short",
            poster=_poster("short.jpg"),
        )
        url = reverse("movie_detail", args=[short_movie.id])
        resp = self.client.get(url)
        self.assertContains(resp, "1h 30min")
