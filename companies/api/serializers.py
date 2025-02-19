from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from companies.models import *
from users.models import User

class CompanyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    image = serializers.ImageField()
    name = serializers.CharField()
    formalName = serializers.CharField(source = "formal_name")
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return obj.user.email if obj.user else ''
    

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
    
class UserCompanyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    companyId = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    is_admin = serializers.BooleanField()
    userImage = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return obj.user.email if obj.user else ''
    
    def get_userId(self, obj):
        return obj.user.id if obj.user else ''
    
    def get_owner(self, obj):
        return obj.company.user.email if obj.company.user else ''
    
    def get_company(self, obj):
        return {"name":obj.company.name,"formalName":obj.company.formal_name} if obj.company else ''
    
    def get_companyId(self, obj):
        return obj.company.id if obj.company else ''
    
    def get_userImage(self, obj):
        if obj.company.user.profile and obj.company.user.profile.image and obj.company.user.profile.image.name:
            request = self.context.get('request')
            image_url = obj.company.user.profile.image.url
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return ''
    
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