from django.contrib.auth.models import User
from rest_framework import serializers

class UserListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name if obj else ''