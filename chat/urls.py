from django.urls import path

from . import views

urlpatterns = [
    # auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_user'),

    # channels
    path('', views.channel_list, name='channel_list'),
    path('channels/create/', views.channel_create, name='channel_create'),
    path('channels/<int:pk>/', views.channel_detail, name='channel_detail'),
    path('channels/<int:pk>/join/', views.channel_join, name='channel_join'),
    path('channels/<int:pk>/leave/', views.channel_leave, name='channel_leave'),
    path('channels/<int:pk>/poll/', views.messages_poll, name='messages_poll'),

    # messages
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),

    # DM
    path('dm/<str:username>/', views.dm_detail, name='dm_detail'),

    # block
    path('block/<str:username>/', views.block_user, name='block_user'),
    path('unblock/<str:username>/', views.unblock_user, name='unblock_user'),

    # moderator
    path('mod/block/<str:username>/', views.mod_block_user, name='mod_block_user'),
    path('mod/unblock/<str:username>/', views.mod_unblock_user, name='mod_unblock_user'),

    # admin
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('panel/channels/', views.admin_channels, name='admin_channels'),
    path('panel/channels/<int:pk>/delete/', views.admin_channel_delete, name='admin_channel_delete'),
]
