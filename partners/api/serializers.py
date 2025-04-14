from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from partners.models import *
from companies.models import Company,UserCompany

class PartnerListSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    image = serializers.ImageField()
    name = serializers.CharField()
    formalName = serializers.CharField(source = "formal_name")
    types = serializers.ListField()
    companyId = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    address = serializers.CharField()
    
    def get_country(self, obj):
        return obj.country.iso2 if obj.country else ''
    
    def get_city(self, obj):
        return obj.city.id if obj.city else ''
    
    def get_country_name(self, obj):
        return obj.country.name if obj.country else ''
    
    def get_city_name(self, obj):
        return obj.city.name if obj.city else ''
    
    def get_companyId(self, obj):
        return obj.company.id if obj.company else ''

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)
        
        return instance