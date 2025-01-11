from django.urls import path, include

from .views import *

app_name = "users"

urlpatterns = [
    path('csrf_token_get/', CSRFTokenGetView.as_view(), name="csrf_token_get"),
    path('login/', UserLoginView.as_view(), name="login"),
    
    path('api/', include("users.api.urls")),
]