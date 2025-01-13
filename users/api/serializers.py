from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from users.models import *

class UserListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name if obj else ''
    
    def get_profile(self, obj):
        return obj.profile.pk if obj.profile else ''
    
    def get_theme(self, obj):
        return obj.profile.theme if obj.profile else ''
    
class UserProfileListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    user = serializers.SerializerMethodField()
    theme = serializers.CharField()
    
    def get_user(self, obj):
        return obj.user.id if obj.user else ''
    
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