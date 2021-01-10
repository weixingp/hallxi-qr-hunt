from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import ProfileUpdateForm


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
            profile.save()
            if has_profile:
                messages.add_message(request, messages.SUCCESS, 'Your profile has been updated.')
            else:
                messages.add_message(request, messages.SUCCESS, 'You have been registered for the game, than you!')
            return redirect("/account/profile/")
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
