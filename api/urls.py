from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *

app_name = 'appApis'

router = DefaultRouter()
router.register(r'Rides', RideViewSet)

urlpatterns = [
    path('Registration',RegistrationApiView.as_view(),name="Registration"),
    path('Login',LoginApiView.as_view(),name="Login"),
    path('', include(router.urls)),

    ]