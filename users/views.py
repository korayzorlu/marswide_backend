from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# Create your views here.



class CSRFTokenGetView(View):
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return JsonResponse({'csrfToken': token})


class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Logged in successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

#@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        print(request.user)
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logged out successfully'})
    
class UserRegisterView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        
        return JsonResponse({'success': True, 'message': 'Logged in successfully'})