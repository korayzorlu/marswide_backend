from django.urls import path, include

from .views import *

app_name = "accounting"

urlpatterns = [
    
    path('', include("accounting.api.urls")),
]