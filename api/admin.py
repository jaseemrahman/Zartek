from django.contrib import admin
from api.models import Ride,CustomUser
# Register your models here.

class RideAdmin(admin.ModelAdmin):
    list_display = ['rider', 'driver', 'pickup_location', 'dropoff_location', 'status', 'created_at']
    search_fields = ['rider__username', 'driver__username', 'pickup_location', 'dropoff_location']
    list_filter = ['created_at', 'status']

admin.site.register(Ride, RideAdmin)

@admin.register(CustomUser)
class CustomUserModelAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'username', 'email', 'phone_number')