from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, label="Email", max_length=255, help_text="Required."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
