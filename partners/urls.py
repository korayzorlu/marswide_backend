from django.urls import path, include

from .views import *

app_name = "partners"

urlpatterns = [

    
    path('', include("partners.api.urls")),
]