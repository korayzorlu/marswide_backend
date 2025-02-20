from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'companies', CompanyList, "companies_api")
router.register(r'user_companies', UserCompanyList, "user_companies_api")

urlpatterns = [
    path('',include(router.urls)),
]
