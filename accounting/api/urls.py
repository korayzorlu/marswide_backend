from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'accounts', AccountList, "accounts_api")

urlpatterns = [
    path('',include(router.urls)),
]
