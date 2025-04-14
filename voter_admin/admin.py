from django.contrib import admin
from .models import AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'admin_name', 'admin_email', 'admin_address', 'admin_acc_created_time')
    search_fields = ('admin_name', 'admin_email', 'admin_address')
    list_filter = ('admin_acc_created_time',)