import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (ChannelForm, DirectMessageForm, MessageForm,
                    ProfileEditForm, RegisterForm, UserRoleForm)
from .models import Channel, CustomUser, DirectMessage, Message, UserBlock


# ---------- helpers ----------

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            messages.error(request, 'Brak uprawnień administratora.')
            return redirect('channel_list')
        return view_func(request, *args, **kwargs)
    return _wrapped


def moderator_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_moderator():
            messages.error(request, 'Brak uprawnień moderatora.')
            return redirect('channel_list')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---------- auth ----------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('channel_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('channel_list')
    else:
        form = RegisterForm()
    return render(request, 'chat/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('channel_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_blocked:
                messages.error(request, 'Twoje konto zostało zablokowane.')
            else:
                login(request, user)
                user.status = 'online'
                user.save(update_fields=['status'])
                return redirect('channel_list')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})


@login_required
def logout_view(request):
    request.user.status = 'offline'
    request.user.save(update_fields=['status'])
    logout(request)
    return redirect('login')


# ---------- profile ----------

@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(CustomUser, username=username)
    else:
        user = request.user
    is_blocked = UserBlock.objects.filter(blocker=request.user, blocked=user).exists()
    return render(request, 'chat/profile.html', {'profile_user': user, 'is_blocked': is_blocked})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil zaktualizowany.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'chat/profile_edit.html', {'form': form})


# ---------- channels ----------

@login_required
def channel_list(request):
    public_channels = Channel.objects.filter(is_public=True).order_by('name')
    my_channels = request.user.channels.order_by('name')

    # DM conversations
    dm_users_ids = (
        DirectMessage.objects
        .filter(Q(sender=request.user) | Q(receiver=request.user))
        .values_list('sender', 'receiver')
    )
    dm_user_ids = set()
    for s, r in dm_users_ids:
        if s != request.user.id:
            dm_user_ids.add(s)
        if r != request.user.id:
            dm_user_ids.add(r)
    dm_users = CustomUser.objects.filter(id__in=dm_user_ids)

    return render(request, 'chat/channel_list.html', {
        'public_channels': public_channels,
        'my_channels': my_channels,
        'dm_users': dm_users,
    })


@login_required
def channel_create(request):
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.created_by = request.user
            channel.save()
            channel.members.add(request.user)
            return redirect('channel_detail', pk=channel.pk)
    else:
        form = ChannelForm()
    return render(request, 'chat/channel_form.html', {'form': form})


@login_required
def channel_detail(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    is_member = channel.members.filter(pk=request.user.pk).exists()

    if request.method == 'POST':
        if not is_member:
            messages.error(request, 'Musisz dołączyć do kanału, żeby pisać.')
            return redirect('channel_detail', pk=pk)
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.channel = channel
            msg.author = request.user
            msg.save()
            return redirect('channel_detail', pk=pk)
    else:
        form = MessageForm()

    msgs = channel.messages.filter(is_deleted=False).select_related('author')
    members = channel.members.all()
    return render(request, 'chat/channel_detail.html', {
        'channel': channel,
        'messages_list': msgs,
        'form': form,
        'is_member': is_member,
        'members': members,
    })


@login_required
def channel_join(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    channel.members.add(request.user)
    return redirect('channel_detail', pk=pk)


@login_required
def channel_leave(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    channel.members.remove(request.user)
    return redirect('channel_list')


@login_required
def messages_poll(request, pk):
    """JSON endpoint — returns messages newer than `since` timestamp."""
    channel = get_object_or_404(Channel, pk=pk)
    since = request.GET.get('since')
    qs = channel.messages.filter(is_deleted=False).select_related('author')
    if since:
        qs = qs.filter(created_at__gt=since)
    data = [
        {
            'id': m.id,
            'author': m.author.username,
            'avatar': m.author.avatar.url if m.author.avatar else None,
            'content': m.content,
            'image': m.image.url if m.image else None,
            'audio': m.audio.url if m.audio else None,
            'created_at': m.created_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({'messages': data})


# ---------- message moderation ----------

@login_required
def message_delete(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if request.user.is_moderator() or msg.author == request.user:
        msg.is_deleted = True
        msg.save(update_fields=['is_deleted'])
    return redirect('channel_detail', pk=msg.channel.pk)


# ---------- DMs ----------

@login_required
def dm_detail(request, username):
    other = get_object_or_404(CustomUser, username=username)
    is_blocked = UserBlock.objects.filter(
        Q(blocker=request.user, blocked=other) | Q(blocker=other, blocked=request.user)
    ).exists()

    if request.method == 'POST' and not is_blocked:
        form = DirectMessageForm(request.POST, request.FILES)
        if form.is_valid():
            dm = form.save(commit=False)
            dm.sender = request.user
            dm.receiver = other
            dm.save()
            return redirect('dm_detail', username=username)
    else:
        form = DirectMessageForm()

    conversation = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)
    ).order_by('created_at')

    return render(request, 'chat/dm_detail.html', {
        'other': other,
        'conversation': conversation,
        'form': form,
        'is_blocked': is_blocked,
    })


# ---------- block ----------

@login_required
def block_user(request, username):
    target = get_object_or_404(CustomUser, username=username)
    if target != request.user:
        UserBlock.objects.get_or_create(blocker=request.user, blocked=target)
    return redirect('profile_user', username=username)


@login_required
def unblock_user(request, username):
    target = get_object_or_404(CustomUser, username=username)
    UserBlock.objects.filter(blocker=request.user, blocked=target).delete()
    return redirect('profile_user', username=username)


# ---------- admin panel ----------

@admin_required
def admin_users(request):
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'chat/admin_users.html', {'users': users})


@admin_required
def admin_user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zaktualizowano użytkownika {user.username}.')
            return redirect('admin_users')
    else:
        form = UserRoleForm(instance=user)
    return render(request, 'chat/admin_user_edit.html', {'form': form, 'edited_user': user})


@admin_required
def admin_channels(request):
    channels = Channel.objects.all().order_by('name')
    return render(request, 'chat/admin_channels.html', {'channels': channels})


@admin_required
def admin_channel_delete(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    channel.delete()
    messages.success(request, 'Kanał usunięty.')
    return redirect('admin_channels')


# ---------- moderator ----------

@moderator_required
def mod_block_user(request, username):
    target = get_object_or_404(CustomUser, username=username)
    target.is_blocked = True
    target.save(update_fields=['is_blocked'])
    messages.success(request, f'Użytkownik {username} zablokowany.')
    return redirect('admin_users')


@moderator_required
def mod_unblock_user(request, username):
    target = get_object_or_404(CustomUser, username=username)
    target.is_blocked = False
    target.save(update_fields=['is_blocked'])
    messages.success(request, f'Użytkownik {username} odblokowany.')
    return redirect('admin_users')
