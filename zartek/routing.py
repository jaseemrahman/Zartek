from channels.routing import ProtocolTypeRouter, URLRouter
from api import consumers  # Import the consumers module

application = ProtocolTypeRouter({
    # Traditional HTTP requests go here
    'http': URLRouter([]),
    # WebSocket connections handled by consumers
    'websocket': URLRouter([
        # Route to the RideTrackerConsumer for ride-specific WebSockets
        ('^/api/rides/(?P<ride_id>[^/]+)/ws/', consumers.RideTrackerConsumer),
    ]),
})
