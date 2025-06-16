from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.validators import RegexValidator


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        max_length=255,
        help_text="Required.",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                message='Enter a valid email address.',
            )
        ],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
