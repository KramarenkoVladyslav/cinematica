from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from movies.models import Movie, Category, Country, Year
from reviews.models import Review

User = get_user_model()
TEST_MEDIA_ROOT = "/tmp/test_media_reviews"


def _poster(name="p.jpg"):
    return SimpleUploadedFile(name, b"\x47\x49\x46", content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SubmitReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.year = Year.objects.create(year=2024)
        cls.country = Country.objects.create(name="USA")
        cls.category = Category.objects.create(name="Film")
        cls.movie = Movie.objects.create(
            title="Review Test Movie",
            description="A movie used for review tests.",
            year=cls.year,
            country=cls.country,
            category=cls.category,
            duration=120,
            trailer_url="https://example.com/trailer",
            poster=_poster("review_movie.jpg"),
        )
        cls.user = User.objects.create_user(username="reviewer", password="pwd12345")
        cls.other_user = User.objects.create_user(username="other", password="pwd12345")

    def setUp(self):
        self.client = Client()

    def _submit_url(self):
        return reverse("submit_review", args=[self.movie.id])

    def test_unauthenticated_user_redirects_to_login(self):
        resp = self.client.post(self._submit_url(), {"rating": 4, "review_text": "Good"})
        self.assertRedirects(resp, f"{reverse('login')}?next={self._submit_url()}")

    def test_valid_review_is_saved(self):
        self.client.login(username="reviewer", password="pwd12345")
        self.client.post(self._submit_url(), {"rating": 4, "review_text": "Great movie!"})
        self.assertTrue(Review.objects.filter(user=self.user, movie=self.movie).exists())

    def test_valid_review_redirects_to_movie_detail(self):
        self.client.login(username="reviewer", password="pwd12345")
        resp = self.client.post(self._submit_url(), {"rating": 5, "review_text": "Loved it!"})
        self.assertRedirects(resp, reverse("movie_detail", args=[self.movie.id]))

    def test_valid_review_increments_review_count(self):
        self.client.login(username="other", password="pwd12345")
        self.movie.refresh_from_db()
        count_before = self.movie.review_count
        self.client.post(self._submit_url(), {"rating": 3, "review_text": "OK"})
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.review_count, count_before + 1)

    def test_duplicate_review_is_blocked(self):
        Review.objects.create(user=self.user, movie=self.movie, rating=5, review_text="First")
        self.client.login(username="reviewer", password="pwd12345")
        self.client.post(self._submit_url(), {"rating": 3, "review_text": "Second attempt"})
        self.assertEqual(Review.objects.filter(user=self.user, movie=self.movie).count(), 1)

    def test_duplicate_review_redirects_to_movie_detail(self):
        Review.objects.create(user=self.user, movie=self.movie, rating=5, review_text="First")
        self.client.login(username="reviewer", password="pwd12345")
        resp = self.client.post(self._submit_url(), {"rating": 3, "review_text": "Dupe"})
        self.assertRedirects(resp, reverse("movie_detail", args=[self.movie.id]))

    def test_rating_above_max_does_not_create_review(self):
        self.client.login(username="reviewer", password="pwd12345")
        self.client.post(self._submit_url(), {"rating": 10, "review_text": "Invalid rating"})
        self.assertFalse(Review.objects.filter(user=self.user, movie=self.movie).exists())

    def test_rating_below_min_does_not_create_review(self):
        self.client.login(username="reviewer", password="pwd12345")
        self.client.post(self._submit_url(), {"rating": 0, "review_text": "Invalid"})
        self.assertFalse(Review.objects.filter(user=self.user, movie=self.movie).exists())

    def test_review_without_text_is_valid(self):
        self.client.login(username="reviewer", password="pwd12345")
        self.client.post(self._submit_url(), {"rating": 3, "review_text": ""})
        self.assertTrue(Review.objects.filter(user=self.user, movie=self.movie).exists())

    def test_nonexistent_movie_returns_404(self):
        self.client.login(username="reviewer", password="pwd12345")
        url = reverse("submit_review", args=[99999])
        resp = self.client.post(url, {"rating": 4, "review_text": "Ghost"})
        self.assertEqual(resp.status_code, 404)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class DeleteReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.year = Year.objects.create(year=2020)
        cls.country = Country.objects.create(name="Germany")
        cls.category = Category.objects.create(name="Series")
        cls.movie = Movie.objects.create(
            title="Delete Test Movie",
            description="A movie used for delete review tests.",
            year=cls.year,
            country=cls.country,
            category=cls.category,
            duration=90,
            trailer_url="https://example.com/trailer2",
            poster=_poster("delete_movie.jpg"),
        )
        cls.owner = User.objects.create_user(username="owner", password="pwd12345")
        cls.intruder = User.objects.create_user(username="intruder", password="pwd12345")

    def setUp(self):
        self.client = Client()
        self.review = Review.objects.create(
            user=self.owner,
            movie=self.movie,
            rating=4,
            review_text="My honest review.",
        )

    def _delete_url(self):
        return reverse("delete_review", args=[self.review.id])

    def test_unauthenticated_user_redirects_to_login(self):
        resp = self.client.post(self._delete_url())
        self.assertRedirects(resp, f"{reverse('login')}?next={self._delete_url()}")
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_owner_can_delete_own_review(self):
        self.client.login(username="owner", password="pwd12345")
        resp = self.client.post(self._delete_url())
        self.assertRedirects(resp, reverse("movie_detail", args=[self.movie.id]))
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_owner_delete_decrements_review_count(self):
        self.client.login(username="owner", password="pwd12345")
        self.movie.refresh_from_db()
        count_before = self.movie.review_count
        self.client.post(self._delete_url())
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.review_count, max(0, count_before - 1))

    def test_non_owner_cannot_delete_review(self):
        self.client.login(username="intruder", password="pwd12345")
        self.client.post(self._delete_url())
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_non_owner_is_redirected_without_deleting(self):
        self.client.login(username="intruder", password="pwd12345")
        resp = self.client.post(self._delete_url())
        self.assertIn(resp.status_code, [200, 302])
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_get_request_does_not_delete_review(self):
        self.client.login(username="owner", password="pwd12345")
        self.client.get(self._delete_url())
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_nonexistent_review_returns_404(self):
        self.client.login(username="owner", password="pwd12345")
        url = reverse("delete_review", args=[99999])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
