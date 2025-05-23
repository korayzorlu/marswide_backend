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

from core.permissions import SubscriptionPermission,BlockBrowserAccessPermission,RequireCustomHeaderPermission

from .serializers import *
from .filters import *

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

class CompanyList(ModelViewSet, QueryListAPIView):
    serializer_class = CompanyListSerializer
    filterset_class = CompanyFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    required_subscription = "free"
    permission_classes = [SubscriptionPermission]
    
    def get_queryset(self):
        custom_related_fields = ["user"]

        queryset = Company.objects.select_related(*custom_related_fields).filter(company_users__is_admin = True, company_users__user = self.request.user).order_by("name")

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name","formalName","user__email"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class UserCompanyList(ModelViewSet, QueryListAPIView):
    serializer_class = UserCompanyListSerializer
    filterset_class = UserCompanyFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    required_subscription = "free"
    permission_classes = [SubscriptionPermission]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        custom_related_fields = ["user","company"]

        queryset = UserCompany.objects.select_related(*custom_related_fields).filter(user = self.request.user).order_by("company__name")

        if not queryset.filter(is_active=True).exists() and queryset.exists():
            first_obj = queryset.first()
            first_obj.is_active = True
            first_obj.save()

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["company__name","user__email"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class UsersInCompanyList(ModelViewSet, QueryListAPIView):
    serializer_class = UsersInCompanyListSerializer
    filterset_fields = {
                        'company': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    required_subscription = "free"
    permission_classes = [SubscriptionPermission]
    
    def get_queryset(self):
        companyId = self.request.query_params.get('companyId')

        custom_related_fields = ["user","company"]

        queryset = UserCompany.objects.select_related(*custom_related_fields).filter(company__id = int(companyId)).order_by("company__name")

        if not queryset.filter(is_active=True).exists() and queryset.exists():
            first_obj = queryset.first()
            first_obj.is_active = True
            first_obj.save()

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["company__name","user__email"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class InvitationList(ModelViewSet, QueryListAPIView):
    serializer_class = InvitationListSerializer
    filterset_fields = {
                        'sender': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    required_subscription = "free"
    permission_classes = [SubscriptionPermission]
    
    def get_queryset(self):
        custom_related_fields = ["sender","recipient","company"]

        queryset = Invitation.objects.select_related(*custom_related_fields).filter(recipient = self.request.user).order_by("id")

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["status","sender__email","recipient__email","company__name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset