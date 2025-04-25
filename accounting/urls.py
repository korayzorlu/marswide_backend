from django.urls import path, include

from .views import *

app_name = "accounting"

urlpatterns = [
    path('add_account/', AddAccountView.as_view(), name="add_account"),
    path('update_account/', UpdateAccountView.as_view(), name="update_account"),
    path('delete_account/', DeleteAccountView.as_view(), name="delete_account"),
    
    path('', include("accounting.api.urls")),
]