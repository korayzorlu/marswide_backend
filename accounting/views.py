from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, FileResponse, HttpResponse

from utils.mixins import CompanyOwnershipRequiredMixin

import json

from .models import *
from .utils import is_valid_account_data

# Create your views here.

class AddAccountView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Auth failed!.','status':'error'}, status=401)
        
        valid, response = is_valid_account_data(data)
        if not valid:
            return response
        
        company = Company.objects.filter(id = data.get('companyId')).first()
        active_company = request.user.user_companies.filter(is_active = True, company = company).first()

        if not company or not active_company:
            return JsonResponse({'message': 'Sorry, something went wrong!','status':'error'}, status=400)
        
        partner = Partner.objects.filter(uuid = data.get('partner')).first()
        currency = Currency.objects.filter(code = data.get('currency') if data.get('currency') else 0).first()

        if Account.objects.filter(partner=partner,currency=currency).exists():
            return JsonResponse({'message': 'An account with this currency already exists for this partner.','status':'error'}, status=400)

        account = Account.objects.create(
            company = company,
            type = data.get('type'),
            partner = partner,
            currency = currency,
        )
        account.save()

        return JsonResponse({'message': 'Created successfully!','status':'success'}, status=200)

class UpdateAccountView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Account
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        valid, response = is_valid_account_data(data)
        if not valid:
            return response

        partner = Partner.objects.filter(uuid = data.get('partner').get('uuid')).first()
        currency = Currency.objects.filter(code = data.get('currency') if data.get('currency') else 0).first()

        obj = Account.objects.filter(uuid = data.get('uuid')).first()
        obj.type = data.get('type')
        obj.partner = partner
        obj.currency = currency
        obj.save()

        return JsonResponse({'message': 'Saved successfully!','status':'success'}, status=200)
    
class DeleteAccountView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Account

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if isinstance(data.get("uuid"),str):
            obj = Account.objects.filter(uuid = data.get('uuid')).first()
            obj.delete()
        elif isinstance(data.get("uuids"),list):
            for uuid in data.get("uuids"):
                obj = Account.objects.filter(uuid = uuid).first()
                obj.delete()

        return JsonResponse({'message': 'Removed successfully!','status':'success'}, status=200)
    
class DeletePartnersView(LoginRequiredMixin,CompanyOwnershipRequiredMixin,View):
    model = Partner

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        uuids = data.get('uuids')

        for uuid in uuids:
            partner = Partner.objects.filter(uuid = uuid).first()
            partner.delete()

        return JsonResponse({'message': 'Removed successfully!','status':'success'}, status=200)
  