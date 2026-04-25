from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Channel, CustomUser, DirectMessage, Message, UserBlock


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': ('role', 'avatar', 'bio', 'is_blocked', 'status')}),
    )
    list_display = ['username', 'email', 'role', 'is_blocked', 'status']
    list_filter = ['role', 'is_blocked']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_public', 'created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'channel', 'content', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'channel']


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'created_at']


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
