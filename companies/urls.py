from django.urls import path, include

from .views import *

app_name = "companies"

urlpatterns = [
    path('add_company/', AddCompanyView.as_view(), name="add_company"),
    path('update_company/', UpdateCompanyView.as_view(), name="update_company"),
    path('delete_company/', DeleteCompanyView.as_view(), name="delete_company"),
    
    path('api/', include("companies.api.urls")),
]