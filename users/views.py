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
        logger = logging.getLogger("django")
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        logger.warning("sdsg")
        user = authenticate(request, username=username, password=password)
        print(request.POST)
        if user is not None:
            login(request, user)
            print(request.user)
            print("oldu lan")
            return JsonResponse({'success': True, 'message': 'Logged in successfully'})
        else:
            print("olsun yine oldu lan")
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)