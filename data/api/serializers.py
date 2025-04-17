from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation
from datetime import datetime, timezone

from companies.models import *
from data.models import Country,City,Currency

class CountryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    formalName = serializers.CharField(source = "formal_name")
    iso2 = serializers.CharField()
    iso3 = serializers.CharField()
    dialCode = serializers.CharField(source = "dial_code")
    emoji = serializers.CharField()
    flag = serializers.CharField()

class CityListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    country = serializers.SerializerMethodField()
    name = serializers.CharField()
    
    def get_country(self, obj):
        return obj.country.name if obj.country else ''
    
class CurrencyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    symbol = serializers.CharField()
    exchange_rate = serializers.DecimalField(max_digits=10,decimal_places=4)