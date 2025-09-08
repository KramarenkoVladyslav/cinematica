from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from .models import Movie, Category, Genre


class MovieModelTests(TestCase):
    def test_movie_creation_success(self):
        category = Category.objects.create(name="Action")
        genre1 = Genre.objects.create(name="Thriller")
        genre2 = Genre.objects.create(name="Adventure")

        poster_file = SimpleUploadedFile(
            name="test.jpg", content=b"fake-image-bytes", content_type="image/jpeg"
        )

        movie = Movie.objects.create(
            title="Test Movie",
            description="Some description",
            year=2024,
            country="USA",
            duration=125,
            poster=poster_file,
            trailer_url="https://example.com/trailer",
            category=category,
        )
        movie.genres.set([genre1, genre2])

        self.assertEqual(Movie.objects.count(), 1)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.category, category)
        self.assertSetEqual(set(movie.genres.all()), {genre1, genre2})
        self.assertEqual(movie.get_duration_in_hours_and_minutes(), "2h 5min")
