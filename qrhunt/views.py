import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import ProfileUpdateForm, UpdateAssignedQuestionForm
from .models import Location, AssignedLocation, Question, AssignedQuestion, Block
from django.utils.timezone import localtime, now
from .main import visit_location, get_user_context, get_random_question


@login_required(login_url='/account/login/')
def check_registered(request):
    user = request.user
    if not hasattr(user, 'profile'):
        return redirect("/account/profile/")
    else:
        # return redirect("/")
        return redirect("/account/profile/")


@login_required(login_url='/account/login/')
def user_details(request):
    template = loader.get_template('account/details.html')
    has_profile = hasattr(request.user, 'profile')
    if request.method == 'POST':
        if not has_profile:
            p_form = ProfileUpdateForm(request.POST)
        else:
            p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if p_form.is_valid():
            profile = p_form.save(commit=False)
            profile.user = request.user
            # profile.block = Block.objects.get(id=p_form.cleaned_data['block'])
            profile.save()
            if has_profile:
                messages.add_message(request, messages.SUCCESS, 'Your profile has been updated.')
            else:
                messages.add_message(request, messages.SUCCESS, 'You have been registered for the game, than you!')
            return redirect("/account/profile/")
        else:
            messages.add_message(request, messages.ERROR, "You have errors in your form, please check.")

    else:
        if not has_profile:
            p_form = ProfileUpdateForm()
        else:
            p_form = ProfileUpdateForm(instance=request.user.profile)

    if len(request.user.socialaccount_set.all()) > 0:
        profile = request.user.socialaccount_set.all()[0]
    else:
        profile = {
            "extra_data": {
                "name": "Invalid Account",
                "email": "null"
            }
        }

    context = {
        "p_form": p_form,
        "profile": profile
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required(login_url='/account/login/')
def location_main(request, uuid):
    template = loader.get_template('core/pages/location.html')
    user = request.user
    success = True
    error = None
    question_id = None

    # Getting location info from QR UUID
    try:
        location = Location.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        context = {
            "success": False,
            "error": "Invalid HallXI BoB location. Please double check your QR code.",
            "uuid": uuid,
            "location": None,
        }
        response = HttpResponse(template.render(context, request))
        return response

    # Check if the location is assigned to the user
    try:
        assigned_location = AssignedLocation.objects.get(
            user=user,
            location=location,
        )

        # Check if the user has visited the location already
        if assigned_location.has_visited:
            success = False
            error = "You have visited this location already."

        # Check if the location has expired.
        if localtime(assigned_location.time).date() != localtime(now()).date():
            success = False
            error = "This location has expired. Locations are refreshed daily. Please check Home page for updated " \
                    "locations."

        # Visit the location if success
        if success:
            question_id = visit_location(user, assigned_location)

    except ObjectDoesNotExist:
        success = False
        error = "This location is not assigned to you. Check Home page for all your assigned locations."

    user_context = get_user_context(request)
    context = {
        "success": success,
        "error": error,
        "uuid": uuid,
        "location": location,
        "question_id": question_id
    }
    ctx = {**user_context, **context}  # Merge context

    response = HttpResponse(template.render(ctx, request))
    return response


@login_required()
def home(request):
    template = loader.get_template('core/pages/home.html')
    user = request.user
    social = user.socialaccount_set.all()[0]

    try:
        assigned_locations = AssignedLocation.objects.filter(user=user, )
    except ObjectDoesNotExist:
        assigned_locations = None

    context = {
        "assigned_locations": assigned_locations,
        "profile": user.profile,
        "social": social,
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required()
def scan_qr(request):
    template = loader.get_template('core/pages/scan.html')

    # Context
    user_context = get_user_context(request)
    context = {
        "test": "",
    }
    ctx = {**user_context, **context}  # Merge context

    response = HttpResponse(template.render(ctx, request))
    return response


@login_required()
def assign_question(request):
    success = False
    message = None
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Illegal access!"
        })

    data = json.loads(request.body.decode("utf-8"))
    form = UpdateAssignedQuestionForm(data)

    user = request.user
    qn_id = data["question_id"]
    if form.is_valid():
        question_slot = AssignedQuestion.objects.get(user=user, id=qn_id, )

        if question_slot.question:
            success = False
            message = "A question for this location has been assigned to you already. Please check main page."
        else:
            difficulty = form.cleaned_data["difficulty"]
            question = get_random_question(user, difficulty)

            if not question:
                success = False
                message = "Sorry, no question with this difficulty is available, please try another difficulty."
            else:
                # Update the assigned question
                question_slot.question = question
                question_slot.save()
                success = True
                message = None
    else:
        success = False
        message = "Something went wrong, please try again later."

    res = {
        "success": success,
        "question_id": qn_id,
        "message": message
    }
    return JsonResponse(res)
