from django.contrib import admin
from django.urls import path
from voter_admin import views

urlpatterns = [
    # sqlite
    path('login/', views.login, name='login'),
    path('login_view/', views.login_view, name='login_view'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_menu/', views.admin_menu, name='admin_menu'),
    path('admin_detail/', views.admin_detail, name='admin_detail'),
    path('admin_change/', views.admin_change, name='admin_change'),
    path('add_candidate/', views.add_candidate, name='add_candidate'),
    path('add_candidate_db/', views.add_candidate_db, name='add_candidate_db'),
    path('change_vote_phase/', views.change_vote_phase, name='change_vote_phase'),
    path('delete_candidate/', views.delete_candidate, name='delete_candidate'),
    path('admin_result_render/', views.admin_result_render, name='admin_result_render'),
    path('admin_title_render/', views.admin_title_render, name='admin_title_render'),
    path('save_election_title/', views.save_election_title, name='save_election_title'),
    path('logout/', views.logout, name='logout'),
    path('block-records/', views.block_records, name='block_records'),
    path('declare-result/', views.declare_result, name='declare_result'),
    path('blocks/', views.block_list),
    path('new_election/', views.new_election,name="new_election"),
    path('change_key/', views.change_key,name="change_key"),
    path('change_key_render/', views.change_key_render,name="change_key_render"),
    path('count_votes/', views.count_votes,name="count_votes"),
    # path('show_result/', views.show_result,name="show_result"),
]