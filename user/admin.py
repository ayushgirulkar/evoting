from django.contrib import admin
from voter_admin.models import Voter

@admin.register(Voter)
class VoterUser(admin.ModelAdmin):
    list_display = ('voter_id', 'address', 'name', 'email', 'mobile','dob','password')
    search_fields = ('address', 'email', 'mobile')