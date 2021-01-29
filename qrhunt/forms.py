from django import forms
from .models import Profile, AssignedQuestion, Question


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


class UpdateAssignedQuestionForm(forms.Form):
    question_uuid = forms.UUIDField()
    DIFFICULTY_CHOICES = Question.DIFFICULTY_CHOICES
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES)


class AnswerQuestionForm(forms.Form):
    question_uuid = forms.UUIDField()
    answer_id = forms.IntegerField()
