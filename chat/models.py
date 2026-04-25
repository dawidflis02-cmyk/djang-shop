from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('user', 'Użytkownik'),
    ]
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    is_blocked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role in ('admin', 'moderator')

    def __str__(self):
        return self.username


class Channel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_channels'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    members = models.ManyToManyField(CustomUser, related_name='channels', blank=True)

    def __str__(self):
        return f'#{self.name}'


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    audio = models.FileField(upload_to='messages/audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.content[:50]}'


class DirectMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_dms')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_dms')
    content = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='dm/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} → {self.receiver}: {self.content[:50]}'


class UserBlock(models.Model):
    blocker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f'{self.blocker} blokuje {self.blocked}'
