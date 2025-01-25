from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import BadHeaderError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

import os

import json
import logging

from .models import *

# Create your views here.



class CSRFTokenGetView(View):
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return JsonResponse({'csrfToken': token})

class UserSessionView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({"authenticated": True})
        return JsonResponse({"authenticated": False})

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
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'name' : user.first_name + " " + user.last_name if user else '',
                'profile':user.profile.pk,
                'theme': user.profile.theme,
                'userSourceCompanies': []
            }
            return JsonResponse({'success': True, 'user':user_data, 'theme': user.profile.theme}, status=200)
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
        username = email.split('@')[0]

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

        user = User.objects.create_user(email=email, username=username, first_name=firstName, last_name=lastName, password=password)
        user.save()

        profile = Profile.objects.create(user = user)
        profile.save()

        user = authenticate(request, email=email, password=password)
        login(request, user)
        user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'name' : user.first_name + " " + user.last_name if user else '',
                'profile':user.profile.pk,
                'theme': user.profile.theme,
                'userSourceCompanies': []
            }
        return JsonResponse({'success': True, 'user':user_data}, status=201)
    
class UserEmailSettingsView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')

        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Auth failed!.'}, status=401)

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            return JsonResponse({'message': 'This email address is already in use.'}, status=400)

        user = request.user
        user.email = email
        user.save()

        return JsonResponse({'success': True}, status=200)
    
class UserPasswordSettingsView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        newPassword = data.get('newPassword')
        newPasswordConfirmation = data.get('newPasswordConfirmation')
        
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Auth failed!.'}, status=401)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if newPassword != newPasswordConfirmation:
                return JsonResponse({'message': 'Please make sure your passwords match.'}, status=400)
            
            try:
                validate_password(newPassword)
            except ValidationError as e:
                return JsonResponse({'message': ' '.join(e.messages)}, status=400)
            
            if password == newPassword:
                return JsonResponse({'message': 'Sorry, your new password cannot be the same as your old password.'}, status=400)
            
            user.set_password(newPassword)
            user.save()
        else:
            return JsonResponse({'message': 'Auth failed! Invalid password.'}, status=400)

        return JsonResponse({'success': True}, status=200)
    
class UserPasswordResetView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')

        form = PasswordResetForm({'email': email})
        if form.is_valid():
            try:
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                context = {
                    'uid' : uid,
                    'token' : token,
                    'protocol': os.getenv("EMAIL_PROTOCOL"),
                    'domain': request.get_host()
                }

                subject = "Password Reset Request for Marswide"
                message = "Please reset your password by clicking the link below."
                html_message = render_to_string('registration/password_reset_email.html', context)
                from_email = "Marswide <info@marswide.com>"
                to_email = [email]
                
                email_message = EmailMessage(
                    subject, 
                    html_message, 
                    from_email, 
                    to_email
                )

                #email_message.body = message  # Metin içeriğini ekle

                email_message.content_subtype = "html"  # HTML içeriği olarak gönder
                email_message.send()
                return JsonResponse({'message': 'Password reset link has been sent.'}, status=200)
            except User.DoesNotExist:
                    return JsonResponse({'message': 'User not found. Please enter a valid email address.'}, status=400)
            except BadHeaderError:
                return JsonResponse({'message': 'Invalid header.'}, status=400)

        return JsonResponse({'message': 'Invalid email.'}, status=400)