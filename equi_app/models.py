
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='custom_groups')
    group_image = models.ImageField(upload_to="group_images/", default="group_images/default.png", blank=True, null=True) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='expenses_participated')
   

    def __str__(self):
        return f"{self.description} - {self.amount}"


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_photos/', default='profile_photos/default.png', blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    upi_id = models.CharField(max_length=64, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    

    def __str__(self):
        return f'Profile of {self.user.username}'
    

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()