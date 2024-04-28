import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ride
from django.db.models import Q

class RideConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None

    async def connect(self):
        # Extract user information from JWT (replace with your logic)
        user_id = self.scope['user'].id

        # Filter rides based on user role (rider or driver)
        rides = Ride.objects.filter(Q(rider_id=user_id) | Q(driver_id=user_id))

        # Create a group name for ride updates (can be improved)
        self.group_name = f"rides_{user_id}"

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Optionally, send initial ride data to the client
        for ride in rides:
            await self.send_ride_data(ride)

        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            # Remove from the group
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle data from client (e.g., update location)
        # ... (implementation depends on your specific needs)

    async def send_ride_data(self, ride):
        data = {
            "id": ride.id,
            "status": ride.status,
            "current_location": ride.current_location,
            # Include other relevant ride details
        }
        await self.send(text_data=json.dumps(data))
