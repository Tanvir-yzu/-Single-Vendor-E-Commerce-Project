from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        default='profile_images/default.jpg'
    )
    address = models.TextField()
    nid_image = models.ImageField(upload_to='nid_images/')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        ordering = ['-created_date']