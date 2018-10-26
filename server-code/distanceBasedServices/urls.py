from django.urls import path
from . import services

urlpatterns = [
	path('',services.services, name='services')
]