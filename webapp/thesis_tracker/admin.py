from django.contrib import admin
from .models import DailyProgress
from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ['user']
admin.site.register(DailyProgress)