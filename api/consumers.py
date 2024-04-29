import json
from channels.generic.websocket import WebsocketConsumer
from .models import Ride
from asgiref.sync import async_to_sync
from json.decoder import JSONDecodeError
from channels.layers import get_channel_layer

class RideConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['ride_id']
        self.room_group_name = 'ride_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print("Received data:", data)

            if 'type' not in data:
                print("Error: 'type' not found in received data.")
                return

            if data['type'] == 'ride_location_update':
                latitude = data.get('latitude')
                longitude = data.get('longitude')

                if latitude is None or longitude is None:
                    print("Error: Latitude or longitude missing in received data.")
                    return

                try:
                    print("Room name:", self.room_name)
                    ride_id = self.room_name
                    ride = Ride.objects.get(pk=ride_id)
                    ride.current_location = f"{latitude},{longitude}"
                    ride.save()
                    print("Ride location updated:", ride)
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'ride_update',
                            'ride_id': ride.id,
                            'latitude': latitude,
                            'longitude': longitude,
                        }
                    )
                except IndexError:
                    print("Error: Room name is not in the expected format.")
                except Ride.DoesNotExist:
                    print("Error: Ride not found with ID:", ride_id)

            else:
                print("Unknown message type:", data['type'])

        except JSONDecodeError as e:
            print("JSONDecodeError:", e)
            print("Error: Malformed JSON data. Please provide valid latitude and longitude.")

    

    def ride_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']
        ride_id= event['ride_id']
        self.send(text_data=json.dumps({
            'type': 'ride_update',
            'latitude': latitude,
            'longitude': longitude,
            'ride_id':ride_id
        }))
    
