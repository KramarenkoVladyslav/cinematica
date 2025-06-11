from django.contrib import admin
from .models import Category, Movie, Genre


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "country", "category")
    list_filter = ("year", "country", "category", "genres")
    search_fields = ("title", "description")
