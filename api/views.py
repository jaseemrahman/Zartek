from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import UserSerializer, LoginSerializer,RideSerializer,RideStatusUpdateSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from api.models import Ride,CustomUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Login API
class LoginApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                return Response({
                    "status": True,
                    "message": 'Logged in successfully.',
                    "token": str(refresh.access_token),
                    "user_details": user_serializer.data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Registration API
class RegistrationApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if CustomUser.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            user = CustomUser.objects.create_user(**serializer.validated_data)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'status': True,
                    'message': 'User created successfully',
                    "token": str(refresh.access_token),
                    "user_details": serializer.data,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Unable to create user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Ride Viewset    
class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RideStatusUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        ride_serializer = RideSerializer(instance)
        return Response({
            'status': True,
            'message': 'Ride status updated successfully',
            'ride_details': ride_serializer.data,
        }, status=status.HTTP_200_OK)
    
class RideAcceptanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def ride_accept(self, request, pk=None):
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Ride does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != ride.driver:
            return Response({
                'status': False,
                'message': 'You do not have permission to perform this action.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if ride.driver_accepted:
            ride.driver_accepted = False
        else:
            ride.driver_accepted = True
        ride.save()
        ride_serializer = RideSerializer(ride)
        return Response({
            'status': True,
            'message': 'Driver acceptance status changed successfully.',
            'ride_details': ride_serializer.data,
        }, status=status.HTTP_200_OK)