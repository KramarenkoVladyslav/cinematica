from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm


def home(request):
    return render(request, "home.html")


def signup(request):
    try:
        if request.method == "POST":
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect("home")
    except Exception as e:
        print(e)

    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})
