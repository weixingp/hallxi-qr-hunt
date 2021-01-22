from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import ProfileUpdateForm
from .models import Location, AssignedLocation, Question, AssignedQuestion, Block
from django.utils.timezone import localtime, now
from .main import visit_location, get_user_context


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
    template = loader.get_template('core/location.html')

    # Getting location info from QR UUID
    try:
        location = Location.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        context = {
            "uuid": uuid,
            "location": "Not found!",
        }
        response = HttpResponse(template.render(context, request))
        return response

    # Check user
    user = request.user
    if not user.profile.has_checked:
        return redirect("/account/invalid")

    # Check if the location is assigned to the user
    try:
        assigned_location = AssignedLocation.objects.get(
            user=user,
            location=location,
            time__day=localtime(now()).day,
        )
    except ObjectDoesNotExist:
        return redirect("/location/access-denied")

    # Check if the user has visited the location already
    if assigned_location.has_visited:
        return redirect("/location/visited")

    # Visit the location
    question_id = visit_location(user, assigned_location)

    context = {
        "uuid": uuid,
        "location": location.name,
        "id": question_id
    }

    response = HttpResponse(template.render(context, request))
    return response


def location_choose_difficulty(request):
    return None


def location_denied(request):
    return None


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
