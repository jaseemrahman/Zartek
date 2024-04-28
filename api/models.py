from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

status_choices = (
    ('REQUESTED','Requested'),
    ('STARTED','Started'),
    ('COMPLETED','Completed'),
    ('CANCELLED','Cancelled'),
)
ROLE_CHOICES = (
    ('1', 'Rider'),
    ('2', 'Driver'),
)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='RIDER')
    current_location = models.CharField(max_length=50, blank=True, null=True) 

class Ride(BaseModel):
    rider = models.ForeignKey(CustomUser, related_name='rider_details', on_delete=models.CASCADE,null=True, blank=True)
    driver = models.ForeignKey(CustomUser, related_name='driver_details',on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.CharField(max_length=100)
    dropoff_location = models.CharField(max_length=100)
    status = models.CharField(max_length=20,default="REQUESTED",choices=status_choices)
    driver_accepted = models.BooleanField(default=False)
    current_location = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = "Ride"

    def __str__(self):
        return str(self.rider.name)