from django.db import models

class ReviewAnalysis(models.Model):
    url = models.URLField(unique=True)
    final_verdict = models.TextField()
    overall_rating = models.FloatField()
    rating_percentages = models.JSONField()  # stores {1: 10, 2: 5, ..., 5: 60}
    top_reviews = models.JSONField()
    keywords = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
