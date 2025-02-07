from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import *

import os
import json

# Create your views here.

class AddCompanyView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get('data', '{}'))
        image = request.FILES.get('image')
        name = data.get('name')
        formal_name = data.get('formalName')

        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Auth failed!.'}, status=401)
        
        if not name or not formal_name:
            return JsonResponse({'message': 'Register failed! Fill required fields.'}, status=400)

        company = Company.objects.create(
            user = request.user,
            name = name,
            formal_name = formal_name
        )

        if image:
            old_image_path = company.image.path if company.image else ""
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            
            filePath = f"images/companies/{company.id}/{image.name}"
            savedPath = default_storage.save(filePath, ContentFile(image.read()))
            company.image = savedPath

        company.save()

        user_companies = request.user.user_companies.all()
        user_companies.update(is_active = False)

        user_company = UserCompany.objects.create(
            user = request.user,
            company = company,
            is_active = True
        )

        user_company.save()

        return JsonResponse({'success': True}, status=200)
    
class UpdateCompanyView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get('data', '{}'))
        image = request.FILES.get('image')
        removeImage = data.get('removeImage')
        name = data.get('name')
        formal_name = data.get('formalName')
        id = data.get('id')
        
        if not name or not formal_name:
            return JsonResponse({'message': 'Register failed! Fill required fields.'}, status=400)
        
        company = Company.objects.filter(id = int(id), user = request.user).first()

        if not company:
            return JsonResponse({'message' : 'Sorry, something went wrong!'}, status=400)

        if image:
            old_image_path = company.image.path if company.image else ""
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            
            filePath = f"images/companies/{company.id}/{image.name}"
            savedPath = default_storage.save(filePath, ContentFile(image.read()))
            company.image = savedPath

        if removeImage:
            old_image_path = company.image.path if company.image else ""
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

            company.image = None

        company.name = name
        company.formal_name = formal_name

        company.save()

        return JsonResponse({'success': True}, status=200)
    
class DeleteCompanyView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        id = data.get('id')
        
        company = Company.objects.filter(id = int(id), user = request.user).first()

        if not company:
            return JsonResponse({'message' : 'Sorry, something went wrong!'}, status=400)

        company.delete()

        return JsonResponse({'success': True}, status=200)