from django.db import models

from django.utils.translation import gettext_lazy as _

from users.models import User
from companies.models import Company

# Create your models here.

class TimestampModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ImportProcess(TimestampModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="import_processes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_import_processes")
    model_name = models.CharField(_("Model Name"), max_length=140)
    task_id = models.CharField(_("Task ID"), max_length=250, unique=True)
    STATUS_CHOICES = (
        ('pending', ('Pending')),
        ('in_progress', ('In Progress')),
        ('completed', ('Completed')),
        ('rejected', ('Rejected'))
    )
    status = models.CharField(_("Status"), max_length=25, default='pending', choices=STATUS_CHOICES, blank=True, null=True)
    progress = models.PositiveIntegerField(_("Progress"), default=0)
    items_count = models.PositiveIntegerField(_("Items Count"), default=0)

    def __str__(self):
        return str(f"{self.model_name} - {self.user.get_full_name()}")