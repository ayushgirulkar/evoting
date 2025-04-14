from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'party', 'position', 'image']  # Remove 'symbol' field

class LoginForm(AuthenticationForm):
    pass