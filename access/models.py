from django.db import models
from django.contrib.auth.models import User

class PageAccess(models.Model):
    """Links a user to a page they can view."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.CharField(max_length=255)

    class Meta:
        unique_together = ("user", "page")

    def __str__(self):
        return f"{self.user.username} → {self.page}"
