from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'mobile_number', 'created_date')
    search_fields = ('user__username', 'name', 'mobile_number')