from .models import Location, AssignedLocation, Question, AssignedQuestion, User
from django.utils.timezone import localtime, now
from random import randint


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


# Get a random question based on the difficulty
def get_random_question(user, difficulty):
    # Get answered/assigned questions of user.
    answered_question = AssignedQuestion.objects \
        .filter(user=user, difficulty=difficulty, ) \
        .values_list('question_id', flat=True)

    # Exclude the questions that have been answered.
    pks = Question.objects.filter(difficulty=difficulty).exclude(id__in=answered_question).values_list('pk',
                                                                                                       flat=True, )

    if len(pks) < 1:
        pks = Question.objects.filter(difficulty=difficulty).values_list('pk', flat=True, )
        if len(pks) < 1:
            return None

    # Get random question of the processed list of questions
    random_idx = randint(0, len(pks) - 1)
    random_qn = Question.objects.get(pk=pks[random_idx])

    return random_qn
