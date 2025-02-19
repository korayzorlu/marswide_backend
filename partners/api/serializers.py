from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from partners.models import *
from companies.models import Company,UserCompany

class PartnerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    image = serializers.ImageField()
    name = serializers.CharField()
    formalName = serializers.CharField(source = "formal_name")
    company = serializers.SerializerMethodField()
    
    def get_company(self, obj):
        return obj.company.name if obj.company else ''

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