# pylint: disable=no-member
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
        )
    image = models.URLField(blank=True)
    
    #models.ImageField(upload_to='images/profile_images/', blank=True)
    

@receiver(models.signals.post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)