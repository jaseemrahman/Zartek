from celery import shared_task
from faker import Faker
from api.models import Ride

@shared_task
def update_ride_locations():
    fake = Faker()
    for ride in Ride.objects.filter(status=Ride.STARTED):
        # Generate simulated location
        latitude = fake.latitude()
        longitude = fake.longitude()
        ride.current_location = models.Point(longitude, latitude)  # Update location using PointField
        ride.save()
