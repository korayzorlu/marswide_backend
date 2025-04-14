from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.signals import request_finished
from django.core.files.base import ContentFile
from django.core.files import File

from PIL import Image
import io
import os

from .models import ImportProcess
from core.middleware import get_current_user

def sendAlert(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
        }
    )

def fetchImportProcesses(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "fetch_import_processes",
            "message": message,
        }
    )

@receiver(pre_save, sender=ImportProcess)
def import_process_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()

    if sender.objects.filter(id=instance.id).exists():
        old_instance = sender.objects.filter(id=instance.id).first()

        if old_instance.status != instance.status:
            if instance.status == "in_progress":
                async_to_sync(channel_layer.group_send)(
                    'private_' + str(instance.user.id),
                    {
                        "type": "fetch_import_processes",
                        "message": {"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}}
                    }
                )
                #fetchImportProcesses({"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}})
            elif instance.status == "completed":
                async_to_sync(channel_layer.group_send)(
                    'private_' + str(instance.user.id),
                    {
                        "type": "fetch_import_processes",
                        "message": {"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}}
                    }
                )
                #fetchImportProcesses({"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}})
                async_to_sync(channel_layer.group_send)(
                    'private_' + str(instance.user.id),
                    {
                        "type": "send_alert",
                        "message": {"message":f"{instance.model_name} items imported successfully!","status":200}
                    }
                )
                #sendAlert({"message":f"{instance.model_name} items imported successfully!","status":200})
            elif instance.status == "rejected":
                async_to_sync(channel_layer.group_send)(
                    'private_' + str(instance.user.id),
                    {
                        "type": "fetch_import_processes",
                        "message": {"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}}
                    }
                )
                #fetchImportProcesses({"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}})
                async_to_sync(channel_layer.group_send)(
                    'private_' + str(instance.user.id),
                    {
                        "type": "send_alert",
                        "message": {"message":f"{instance.model_name} items import rejected due to invalid data!","status":400}
                    }
                )
                #sendAlert({"message":f"{instance.model_name} items import rejected due to invalid data!","status":400})

        if old_instance.progress != instance.progress:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(instance.user.id),
                {
                    "type": "send_import_process_percent",
                    "message": {"progress":instance.progress,"task":instance.task_id}
                }
            )

@receiver(post_delete, sender=ImportProcess)
def import_process_delete(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'private_' + str(instance.user.id),
        {
            "type": "fetch_import_processes",
            "message": {"status":instance.status,"model":instance.model_name,"activeCompany": {"id":instance.company.id}}
        }
    )