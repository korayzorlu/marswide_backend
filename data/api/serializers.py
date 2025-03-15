from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation
from datetime import datetime, timezone

from companies.models import *
from data.models import Country

class CountryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    formalName = serializers.CharField(source = "formal_name")
    iso2 = serializers.CharField()
    iso3 = serializers.CharField()
    dialCode = serializers.CharField(source = "dial_code")
    emoji = serializers.CharField()
    flag = serializers.CharField()
    
    
