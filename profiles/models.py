from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    iserv_domain = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, blank=True)
    accept_agb = models.BooleanField(default=True)
    accept_dse = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username