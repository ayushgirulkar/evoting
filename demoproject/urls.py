"""
URL configuration for demoproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index, name='index'),
    path('index/', views.index ,name='index'),
    path('home/',views.home, name='home'),
    # path('login_view/',views.login_view ,name='login_view'),
    # path('demo/',views.demo, name='index'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),

    # Admin app urls
    path('voter_admin/',include('voter_admin.urls')),
    path('user/', include('user.urls')),
]
