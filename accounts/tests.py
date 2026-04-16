from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_redirects_to_movie_list(self):
        resp = self.client.get(reverse("home"))
        self.assertRedirects(resp, reverse("movie_list"), fetch_redirect_response=False)

    def test_home_redirects_when_authenticated(self):
        User.objects.create_user(username="someone", password="pwd12345")
        self.client.login(username="someone", password="pwd12345")
        resp = self.client.get(reverse("home"))
        self.assertRedirects(resp, reverse("movie_list"), fetch_redirect_response=False)


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup")
        self.valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "Securepass123!",
            "password2": "Securepass123!",
        }

    def test_get_renders_signup_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/signup.html")
        self.assertIn("form", resp.context)

    def test_valid_signup_creates_user(self):
        self.client.post(self.url, self.valid_data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_valid_signup_redirects_to_movie_list(self):
        resp = self.client.post(self.url, self.valid_data)
        self.assertRedirects(resp, reverse("movie_list"), fetch_redirect_response=False)

    def test_valid_signup_logs_user_in(self):
        self.client.post(self.url, self.valid_data)
        resp = self.client.get(reverse("home"))
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_duplicate_username_does_not_create_second_user(self):
        User.objects.create_user(username="newuser", password="pwd12345")
        resp = self.client.post(self.url, self.valid_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_mismatched_passwords_does_not_create_user(self):
        data = {**self.valid_data, "password2": "DifferentPass456!"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_single_char_username_is_rejected(self):
        data = {**self.valid_data, "username": "a"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="a").exists())

    def test_username_with_spaces_is_rejected(self):
        data = {**self.valid_data, "username": "new user"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="new user").exists())

    def test_missing_email_does_not_create_user(self):
        data = {**self.valid_data, "email": ""}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_invalid_email_format_is_rejected(self):
        data = {**self.valid_data, "email": "not-an-email"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())
