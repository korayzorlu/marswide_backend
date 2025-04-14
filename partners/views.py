from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, FileResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from utils.mixins import CompanyOwnershipRequiredMixin

from .models import *
from common.models import ImportProcess
from common.utils import BaseImporter
from .tasks import importPartners

import os
import json
import pandas as pd

# Create your views here.

def sendAlert(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
        }
    )

class AddPartnerView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Auth failed!.'}, status=401)
        
        if not data.get('name') or not data.get('formalName'):
            return JsonResponse({'message': 'Fill required fields.'}, status=400)
        
        company = Company.objects.filter(id = data.get('companyId')).first()
        active_company = request.user.user_companies.filter(is_active = True, company = company).first()

        if not company or not active_company:
            return JsonResponse({'message': 'Sorry, something went wrong!'}, status=400)

        country = Country.objects.filter(iso2 = data.get('country')).first()
        city = City.objects.filter(country__iso2 = data.get('country'),id = data.get('city')).first()

        partner = Partner.objects.create(
            company = company,
            name = data.get('name'),
            formal_name = data.get('formalName'),
            country = country,
            city = city,
            address = data.get('address')
        )
        partner.save()

        return JsonResponse({'message': 'Created successfully!'}, status=200)
    
class UpdatePartnerView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Partner
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if not data.get('name') or not data.get('formalName'):
            return JsonResponse({'message': 'Fill required fields.'}, status=400)

        country = Country.objects.filter(iso2 = data.get('country') if data.get('country') else 0).first()
        city = City.objects.filter(country__iso2 = data.get('country') if data.get('country') else 0,id = int(data.get('city')) if data.get('city') else 0).first()

        partner = Partner.objects.filter(uuid = data.get('uuid')).first()
        
        partner.name = data.get('name')
        partner.formal_name = data.get('formalName')
        partner.country = country if country else None
        partner.city = city if city else None
        partner.address = data.get('address')
        partner.save()

        return JsonResponse({'message': 'Saved successfully!'}, status=200)
    
class DeletePartnerView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Partner

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        partner = Partner.objects.filter(uuid = data.get('uuid')).first()
        partner.delete()

        return JsonResponse({'message': 'Removed successfully!'}, status=200)
    
class DeletePartnersView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Partner

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        uuids = data.get('uuids')

        for uuid in uuids:
            partner = Partner.objects.filter(uuid = uuid).first()
            partner.delete()

        return JsonResponse({'message': 'Removed successfully!'}, status=200)
    
class PartnersTemplateView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "static", "files", "partners-template.xlsx")
        
        if not os.path.exists(file_path):
            return JsonResponse({'message': 'File not found!'}, status=404)

        return FileResponse(open(file_path, 'rb'))
    
class ImportPartnersView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get('data', '{}'))
        file = request.FILES.get('file')
        
        importer = BaseImporter(user_id=request.user.id, app="partners", model_name="Partner", file=file)

        if importer.validate_file() != 200:
            return JsonResponse(importer.validate_file(), status=400)

        sendAlert({"message":"Items importing on background...","status":200})

        df_json = importer.read_file()
        if isinstance(importer.read_file(), dict):
            return JsonResponse(df_json, status=400)
            
        importer.start_import(df_json)

        return HttpResponse(status=200)