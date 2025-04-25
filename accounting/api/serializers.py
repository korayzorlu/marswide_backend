from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from accounting.models import *

class AccountListSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    companyId = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    type = serializers.CharField()
    balance = serializers.DecimalField(max_digits=14,decimal_places=2)
    
    def get_companyId(self, obj):
        return obj.company.id if obj.company else ''

    def get_partner(self, obj):
        return {"uuid":obj.partner.uuid,"name":obj.partner.name} if obj.partner else {}
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    # def get_type(self, obj):
    #     return obj.get_type_display()

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