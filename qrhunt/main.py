from .models import Location, AssignedLocation, Question, AssignedQuestion
from django.utils.timezone import localtime, now


def get_question(user):
    return None


def visit_location(user, assigned_location):
    # Mark the location as visited
    assigned_location.has_visited = True
    assigned_location.visit_time = localtime(now())
    assigned_location.save()

    # Assign a question slot to the user
    # Actual question will be assigned when user choose a difficulty
    new_question = AssignedQuestion.objects.create(
        user=user,
    )

    return new_question.id


def get_user_context(request):
    user = request.user
    social = user.socialaccount_set.all()[0]

    context = {
        "profile": user.profile,
        "social": social,
    }

    return context