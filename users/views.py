from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import *

# Create your views here.



class CSRFTokenGetView(View):
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return JsonResponse({'csrfToken': token})


class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
                request.session.modified = True
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'message': 'Login failed! Invalid username or password.'}, status=401)

#@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'success': True})
    
class UserRegisterView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        passwordConfirmation = data.get('passwordConfirmation')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        refCode = data.get('refCode')

        if not email or not password or not passwordConfirmation or not firstName or not lastName or not refCode:
            return JsonResponse({'message': 'Register failed! Fill required fields.'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Register failed! This email address is already in use.'}, status=400)
        
        if password != passwordConfirmation:
            return JsonResponse({'message': 'Register failed! Please make sure your passwords match.'}, status=400)
        
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({'message': ' '.join(e.messages)}, status=400)
        
        if refCode != "MARS2030SDXF":
            return JsonResponse({'message': 'Register failed! Invalid reference code'}, status=400)

        user = User.objects.create_user(email=email, username=email, password=password)
        user.save()

        profile = Profile.objects.create(user = user)
        profile.save()

        user = authenticate(request, email=email, password=password)
        login(request, user)
        return JsonResponse({'success': True}, status=201)