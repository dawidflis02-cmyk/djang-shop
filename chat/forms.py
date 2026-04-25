from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Channel, CustomUser, DirectMessage, Message


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar', 'bio', 'email']


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'description', 'is_public']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image', 'audio']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Napisz wiadomość...', 'autocomplete': 'off'}),
        }


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content', 'image']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Napisz wiadomość...', 'autocomplete': 'off'}),
        }


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role', 'is_blocked']
