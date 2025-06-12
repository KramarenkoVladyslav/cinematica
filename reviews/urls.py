from django.urls import path
from . import views

urlpatterns = [
    path("submit_review/<int:movie_id>/", views.submit_review, name="submit_review"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
]
