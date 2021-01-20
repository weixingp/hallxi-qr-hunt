from django import forms
from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['fullname', 'block', 'level', 'room_number', 'mobile']

    display_name = {
        "fullname": "Full name",
        "block": "Block",
        "level": "Level",
        "room_number": "Room number",
        "mobile": "Mobile Number"
    }
