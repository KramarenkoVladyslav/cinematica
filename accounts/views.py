from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)

                return redirect("home")

            except Exception as e:
                logger.error(f"Error during signup: {e}")
                messages.error(request, "An error occurred during registration.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})
