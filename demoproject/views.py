from django.http import HttpResponse
from django.shortcuts import render
import mysql.connector as sql
from django.shortcuts import render, redirect
from django.contrib.auth.models import User  # For password hashing

def index(request):
    return render(request, 'index.html')


def login(request):
	return render(request,"login.html")

def logout(request):
    return render(request,"index.html")

def home(request):
	return render(request,"voter/voter_menu.html")

def signup(request):
    return HttpResponse('Done Signup')

def contact(request):
    return render(request,"contact.html")

def services(request):
    return render(request,"service.html")

def about(request):
    return render(request,"about.html")