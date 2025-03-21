from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework_datatables.filters import DatatablesFilterBackend

from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import CharFilter
from rest_framework.response import Response
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status

from .serializers import *

from users.models import Profile

class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend)
            return super().get_queryset()
        queryset = self.queryset

        # check the start index is integer
        try:
            start = self.request.GET.get('start')
            start = int(start) if start else None
        # else make it None
        except ValueError:
            start = None

        # check the end index is integer
        try:
            end = self.request.GET.get('end')
            end = int(end) if end else None
        # else make it None
        except ValueError:
            end = None

        # skip filters and sorting if they are not exists in the model to ensure security
        accepted_filters = {}
        # loop fields of the model
        for field in queryset.model._meta.get_fields():
            # if field exists in request, accept it
            if field.name in dict(self.request.GET):
                accepted_filters[field.name] = dict(self.request.GET)[field.name]
            # if field exists in sorting parameter's value, accept it

        filters = {}

        for key, value in accepted_filters.items():
            if any(val in value for val in EMPTY_VALUES):
                if queryset.model._meta.get_field(key).null:
                    filters[key + '__isnull'] = True
                else:
                    filters[key + '__exact'] = ''
            else:
                filters[key + '__in'] = value
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all().filter(**filters)[start:end]
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            elif self.request.GET.get('format', None) == 'datatables':
                self._paginator = self.pagination_class()
            else:
                self._paginator = None
        return self._paginator

class UserList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = UserListSerializer
    filterset_fields = {
                        'username': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["profile"]

        type = self.kwargs.get('type', None)

        if type == "current":
            queryset = User.objects.filter(id = self.request.user.id)
        else:
            queryset = User.objects.select_related(*custom_related_fields).all().order_by("first_name","last_name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["username","first_name","last_name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)')
    def filter_by_type(self, request, type=None):
        """
        Custom action to filter by type.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserProfileList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = UserProfileListSerializer
    filterset_fields = {
                        'user': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["user"]

        queryset = Profile.objects.select_related(*custom_related_fields).all().order_by("user__username")

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["user__username"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
