from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='/accounts/login/')
def check_registered(request):
    user = request.user
    if not user.is_registered:
        return redirect("/accounts/signup/details/")
    else:
        return redirect("/")


@login_required(login_url='/accounts/login/')
def user_details(request):
    template = loader.get_template('account/details.html')
    user = request.user
    context = {
        "email": user.email,
        "hp": user.hp,
    }
    response = HttpResponse(template.render(context, request))
    return response
