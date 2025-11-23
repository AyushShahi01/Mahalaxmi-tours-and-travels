
from django.db import models

class Package(models.Model):
    package_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(default=1, help_text="Duration in days")
    group_size = models.PositiveIntegerField(default=10, help_text="Maximum group size")
    start_date = models.DateField()
    cover_image = models.CharField(max_length=500, blank=True, null=True, help_text="Image URL or path")
    tour_highlights = models.JSONField()  # list of strings
    tour_details = models.JSONField()     # list of strings or steps

    def __str__(self):
        return self.title
