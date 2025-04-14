from django.contrib import admin
from django.urls import include, path

from django.contrib import admin
from user import views

urlpatterns = [
    # redirection urls voter
    path('voter_reg/', views.voter_reg, name='voter_reg'),
    path('voter_signup/', views.voter_signup, name='voter_signup'),
    path('voter_menu/', views.voter_menu, name='voter_menu'),
    path('voter_voting/', views.voter_voting, name='voter_voting'),
    path('voter_result/', views.voter_result, name='voter_result'),
    path('voter_login/', views.voter_login, name='voter_login'),
    path('voter_login_view/', views.voter_login_view, name='voter_login_view'),
    path('signup_view/', views.signup_view, name='signup_view'),
    path('signup_session/', views.signup_session,name='signup_session'),
    path('email_verify/', views.email_verify,name='email_verify'),
    path('verify_signup/', views.verify_signup,name='verify_signup'),
    path('vote/', views.vote, name='vote'),
    path('otp_reg/', views.otp_reg, name='otp_reg'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('live_feed/', views.live_feed, name='live_feed'),
    path('start_stream/', views.start_stream, name='start_stream'),
    path('count_votes_per_candidate/', views.count_votes_per_candidate),
]
