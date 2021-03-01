from django import forms
from .models import Profile, AssignedQuestion, Question, PhotoUpvote, PhotoComment, PhotoSubmission


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


class UseItemForm(forms.Form):
    item_id = forms.IntegerField()
    block_id = forms.IntegerField()


class CastVoteForm(forms.ModelForm):
    class Meta:
        model = PhotoUpvote
        fields = ['submission']


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ['comment', 'submission']


class DeletePhotoCommentForm(forms.Form):
    comment_id = forms.IntegerField()


class NewPhotoSubmissionForm(forms.ModelForm):
    class Meta:
        model = PhotoSubmission
        fields = ['photo', 'photo2', 'photo3', 'title']
