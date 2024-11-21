from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='genre_images/', blank=True, null=True)  # Image for the genre

    def str(self):
        return self.name