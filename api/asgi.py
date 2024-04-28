import json
from channels.generic.websocket import WebsocketConsumer
from .models import Ride

class RideTrackerConsumer(WebsocketConsumer):

    def connect(self):
        ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.ride_group_name = f'ride_{ride_id}'

        # Join the group for this specific ride
        async_group = self.channel_layer.group_add(
            self.ride_group_name,
            self.channel_name
        )

        await self.accept(async_group)

    def disconnect(self, close_code):
        # Leave the group
        async_group = self.channel_layer.group_discard(
            self.ride_group_name,
            self.channel_name
        )

        await async_group

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Handle received data (e.g., update ride location in model)
        # Simulate location update for now
        new_location = {'latitude': 40.7128, 'longitude': -74.0059}  # Example coordinates
        ride = Ride.objects.get(pk=int(text_data_json['ride_id']))
        ride.current_location = new_location
        ride.save()

        # Broadcast the update to all connected clients in the group
        update_message = text_data_json
        async_group = self.channel_layer.group_send(
            self.ride_group_name,
            {
                'type': 'ride.update',
                'message': update_message,
            }
        )

        await async_group

    def ride_update(self, event):
        update_message = event['message']

        
