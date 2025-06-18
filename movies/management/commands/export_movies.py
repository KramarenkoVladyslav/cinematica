from django.core.management.base import BaseCommand
from movies.models import Movie
import csv

class Command(BaseCommand):
    help = 'Export all movies to a CSV file'

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        with open('movies_export.csv', 'w', newline='') as csvfile:
            fieldnames = ['title', 'description', 'year', 'country', 'duration', 'trailer_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for movie in movies:
                writer.writerow({
                    'title': movie.title,
                    'description': movie.description,
                    'year': movie.year,
                    'country': movie.country,
                    'duration': movie.duration,
                    'trailer_url': movie.trailer_url,
                })

        self.stdout.write(self.style.SUCCESS('Successfully exported movies to movies_export.csv'))