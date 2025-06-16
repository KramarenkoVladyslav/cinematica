from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.validators import RegexValidator


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, label="Email", max_length=255, help_text="Required."
    )

    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9_.+-]{2,}$",
                message="Username must contain at least two characters.",
            )
        ],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
