import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from hallxiqr.settings import IS_PHASE2
from .forms import ProfileUpdateForm, UpdateAssignedQuestionForm, AnswerQuestionForm, UseItemForm, CastVoteForm, \
    PhotoCommentForm, DeletePhotoCommentForm, NewPhotoSubmissionForm, DeletePhotoSubmissionForm
from .models import Location, AssignedLocation, Question, AssignedQuestion, Block, Answer, AssignedLootBox, \
    AssignedItem, PhotoSubmission, PhotoUpvote, PhotoComment
from django.utils.timezone import localtime, now
from .main import visit_location, get_user_context, get_random_question, assign_loot_box, get_block_hp, \
    get_block_exploration, use_item as use, open_loot_box, get_total_blk_player, get_unanswered_qn


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
    question_uuid = None

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
            question_uuid = visit_location(user, assigned_location)

    except ObjectDoesNotExist:
        success = False
        error = "This location is not assigned to you. Check Home page for all your assigned locations."

    user_context = get_user_context(request)
    context = {
        "success": success,
        "error": error,
        "uuid": uuid,
        "location": location,
        "question_uuid": question_uuid
    }
    ctx = {**user_context, **context}  # Merge context

    response = HttpResponse(template.render(ctx, request))
    return response


@login_required()
def home(request):
    template = loader.get_template('core/pages/home.html')
    user = request.user

    try:
        assigned_locations = AssignedLocation.objects.filter(user=user, )
    except ObjectDoesNotExist:
        assigned_locations = None

    photo_submissions = PhotoSubmission.objects.filter(has_reviewed=True).order_by('-time')

    for submission in photo_submissions:
        submission.votes = PhotoUpvote.objects.filter(submission=submission).count()

    my_submission = PhotoSubmission.objects.filter(user=user)
    if my_submission:
        my_submission = my_submission[0]
        my_submission.votes = PhotoUpvote.objects.filter(submission=my_submission).count()

    context = {
        "is_phase2": IS_PHASE2,
        "assigned_locations": assigned_locations,
        "profile": user.profile,
        "blk_hp": get_block_hp(user.profile.block),
        "blk_exploration": get_block_exploration(user.profile.block),
        "total_member": get_total_blk_player(user.profile.block),
        "unanswered_questions": get_unanswered_qn(user),
        "photo_submissions": photo_submissions,
        "my_submission": my_submission,
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
    qn_uuid = None

    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Illegal access!"
        })

    data = json.loads(request.body.decode("utf-8"))
    form = UpdateAssignedQuestionForm(data)

    user = request.user
    if form.is_valid():
        qn_uuid = data["question_uuid"]
        question_slot = AssignedQuestion.objects.get(user=user, uuid=qn_uuid, )

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
                question_slot.time = localtime(now())
                question_slot.save()
                success = True
                message = None
    else:
        success = False
        message = "Something went wrong, please try again later."

    res = {
        "success": success,
        "question_uuid": qn_uuid,
        "message": message
    }
    return JsonResponse(res)


@login_required()
def question_page(request, uuid):
    template = loader.get_template('core/pages/question.html')
    user = request.user
    # Getting question from url uuid
    try:
        assigned_question = AssignedQuestion.objects.get(uuid=uuid)
        question = assigned_question.question
    except ObjectDoesNotExist:
        context = {
            "success": False,
            "error": "Invalid Question ID.",
        }
        response = HttpResponse(template.render(context, request))
        return response

    if assigned_question.user != user:
        context = {
            "success": False,
            "error": "This question does not belong to you. Check that you have logged in to the right account.",
        }
        response = HttpResponse(template.render(context, request))
        return response
    elif assigned_question.has_answered:
        context = {
            "success": False,
            "error": "You have answered this question already.",
        }
        response = HttpResponse(template.render(context, request))
        return response
    elif localtime(assigned_question.time).date() != localtime(now()).date():
        context = {
            "success": False,
            "error": "This question has expired.",
        }
        response = HttpResponse(template.render(context, request))
        return response

    question_options = list(Answer.objects.filter(question=question))

    context = {
        "success": True,
        "question_uuid": uuid,
        "question": question,
        "options": question_options
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required()
def answer_question(request):
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Illegal access!"
        })

    form = AnswerQuestionForm(request.POST)
    user = request.user

    if not form.is_valid():
        success = False
        message = "Please select an answer."
        return JsonResponse({
            "success": success,
            "message": message,
        })

    qn_uuid = form.cleaned_data["question_uuid"]
    answer_id = form.cleaned_data["answer_id"]

    try:
        question_slot = AssignedQuestion.objects.get(uuid=qn_uuid)
    except ObjectDoesNotExist:
        success = False
        message = "Invalid question ID, please seek assistance from game chat group."
        return JsonResponse({
            "success": success,
            "message": message,
        })

    if question_slot.user != user:
        context = {
            "success": False,
            "message": "This question does not belong to you. Check that you have logged in to the right account.",
        }
        return JsonResponse(context)
    elif question_slot.has_answered:
        context = {
            "success": False,
            "message": "You have answered this question already.",
        }
        return JsonResponse(context)

    question = question_slot.question
    answer = Answer.objects.filter(question=question).filter(id=answer_id)
    if len(answer) > 0:
        answer = answer[0]
        success = True
        # Marked as answered
        question_slot.has_answered = True
        question_slot.answered_time = localtime(now())
        question_slot.save()

        if answer.is_correct:
            # Assign loot box
            if question.difficulty == "1":
                # Easy qn
                loot_box_amt = 1
            elif question.difficulty == "2":
                # Normal qn
                loot_box_amt = 2
            elif question.difficulty == "3":
                # Hard qn
                loot_box_amt = 3
            else:
                loot_box_amt = 0

            assign_loot_box(user, loot_box_amt)
            correct = True
            message = "You have received " + str(loot_box_amt) + " loot box(es)."
        else:
            correct = False
            if question.type == "1":
                # Covid-19 questions -> show correct answer
                correct_answer = Answer.objects.filter(question=question).filter(is_correct=True)[0]
                message = "Oops, the correct answer is " + correct_answer.answer + "."
            else:
                # HallXI questions -> don't show answer
                message = "Oops, take some time to explore Hall XI more!!!"

    else:
        success = False
        message = "Invalid answer id, please seek assistance from game chat group."
        correct = False

    context = {
        "success": success,
        "message": message,
        "correct": correct,
    }

    return JsonResponse(context)


@login_required()
def inventory(request):
    template = loader.get_template('core/pages/item.html')
    user = request.user

    # Get a list of unopened loot boxes
    loot_box_count = AssignedLootBox.objects.filter(user=user, has_opened=False).count()

    # Get a list of unused items
    item_list = list(AssignedItem.objects.filter(user=user, has_used=False).exclude(item=None))
    attack_items = []
    heal_items = []
    special_items = []
    for item in item_list:
        if item.item.type == "1":
            attack_items.append(item)
        elif item.item.type == "2":
            heal_items.append(item)
        else:
            special_items.append(item)

    context = {
        "loot_box_count": loot_box_count,
        "attack_items": attack_items,
        "heal_items": heal_items,
        "special_items": special_items
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required
def use_item(request):
    if request.method != "POST":
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    form = UseItemForm(request.POST)
    info = None
    if form.is_valid():
        try:
            item = AssignedItem.objects.get(id=form.cleaned_data["item_id"])
            block = Block.objects.get(id=form.cleaned_data["block_id"])
        except ObjectDoesNotExist:
            success = False
            message = "Invalid item/block ID."
            return JsonResponse({"success": success, "message": message})

        res = use(user, item, block)

        success = res["success"]
        message = res["message"]
        info = {
            "block": block.name,
            "hp": res["hp"],
        }

    else:
        success = False
        message = "Incomplete selection."

    return JsonResponse({"success": success, "message": message, "info": info})


@login_required()
def get_blocks_stats(request):
    if request.method != 'GET':
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})
    elif not request.GET.get('type'):
        success = False
        message = "Invalid params"
        return JsonResponse({"success": success, "message": message})

    req_type = request.GET.get('type')
    user = request.user
    block_list = Block.objects.all().order_by('name')
    user_blk = user.profile.block

    if req_type == "exclude-user":
        block_list = block_list.exclude(id=user_blk.id)
    elif req_type == "only-user":
        block_list = block_list.filter(id=user_blk.id)

    blocks = {}
    for block in block_list:
        hp = get_block_hp(block)
        exploration = get_block_exploration(block)
        blocks[block.name] = {
            "id": block.id,
            "curr_hp": hp[0],
            "max_hp": hp[1],
            "curr_exploration": exploration[0],
            "max_exploration": exploration[1],
        }

    success = True
    context = {
        "success": success,
        "blocks": blocks,
        "message": None
    }

    return JsonResponse(context)


def loot_box(request):
    template = loader.get_template('core/pages/lootbox.html')
    user = request.user
    loot_box_list = AssignedLootBox.objects.filter(user=user, has_opened=False)

    context = {
        "count": len(loot_box_list),
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required()
def open_loot_box_view(request):
    if request.method != 'GET':
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    loot_box_list = AssignedLootBox.objects.filter(user=user, has_opened=False)

    if len(loot_box_list) < 1:
        success = False
        message = "You don't have any loot boxes to open."
        return JsonResponse({"success": success, "message": message})

    item_list = []
    for box in loot_box_list:
        new_item = open_loot_box(box)
        item = {
            "id": new_item.id,
            "image": new_item.image.url,
            "name": new_item.name,
            "type": new_item.get_type_display(),
            "rarity": new_item.get_rarity_display(),
        }
        item_list.append(item)

    success = True
    items = item_list

    return JsonResponse({"success": success, "items": items})


def landing_page(request):
    template = loader.get_template('account/landing.html')

    context = {
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required()
def photo_submission_view_page(request, submission_id):
    template = loader.get_template('core/pages/photo-view.html')
    user = request.user

    try:
        submission = PhotoSubmission.objects.get(id=submission_id)
        upvote = PhotoUpvote.objects.filter(user=user, submission=submission).count()

        # Comments
        comments = PhotoComment.objects.filter(submission=submission).order_by('-time')
        if not submission.has_reviewed and submission.user != user:
            submission = None
            upvote = None
            comments = None
            message = "This submission is under review, check back shortly."
        else:
            message = "Success"
    except ObjectDoesNotExist:
        submission = None
        upvote = None
        comments = None
        message = "This submission does not exist or has been deleted."

    context = {
        "submission": submission,
        "upvote": upvote,
        "user": user,
        "comments": comments,
        "message": message
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required()
def vote_view(request):
    if request.method != "POST":
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    form = CastVoteForm(request.POST)
    if form.is_valid():
        has_voted = PhotoUpvote.objects.filter(user=user, submission=form.cleaned_data['submission']).count()
        if not has_voted:
            upvote = form.save(commit=False)
            upvote.user = user
            upvote.save()

            success = True
            message = "voted"
        else:
            success = False
            message = "You have voted on this submission."
    else:
        success = False
        message = "Incomplete submission, please try again."

    return JsonResponse({"success": success, "message": message})


@login_required()
def comment_view(request):
    if request.method != "POST":
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    form = PhotoCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = user
        comment.save()

        success = True
        message = comment.id
    else:
        success = False
        message = "Incomplete submission, please try again."

    return JsonResponse({"success": success, "message": message})


@login_required()
def comment_delete_view(request):
    if request.method != "POST":
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    form = DeletePhotoCommentForm(request.POST)
    if form.is_valid():
        try:
            comment = PhotoComment.objects.get(user=user, id=form.cleaned_data["comment_id"])
            comment.delete()
            success = True
            message = "Comment deleted."
        except ObjectDoesNotExist:
            success = False
            message = "Comment does not exist or has been deleted. Reload the page."
    else:
        success = False
        message = "Incomplete submission, please try again."

    return JsonResponse({"success": success, "message": message})


@login_required()
def photo_submission_new_page(request):
    template = loader.get_template('core/pages/new-photo-submission.html')
    user = request.user

    if request.method == "GET":
        has_submitted = PhotoSubmission.objects.filter(user=user)
        if has_submitted:
            message = "You have already submitted one entry. To submit a new entry, please delete the old entry " \
                      "<a href='/submission/" + str(has_submitted[0].id) +"'>here</a>."
        else:
            message = "OK"
        context = {
            "has_submitted": has_submitted,
            "message": message,
        }

        response = HttpResponse(template.render(context, request))
        return response
    elif request.method == "POST":
        print(request.POST)
        form = NewPhotoSubmissionForm(request.POST, files=request.FILES)
        if form.is_valid():
            has_submitted = PhotoSubmission.objects.filter(user=user)
            if has_submitted:
                success = False
                submission_id = has_submitted[0].id
                message = "You have already submitted one entry. <a href='/submission/" + str(submission_id) +"'>View here</a>"
            else:
                submission = form.save(commit=False)
                submission.user = user
                submission.save()
                success = True
                message = "Submitted"
                submission_id = submission.id
        else:
            success = False
            message = "Incomplete submission, please try again."
            submission_id = None
            print(form.errors)

        return JsonResponse({"success": success, "message": message, "submission_id": submission_id})
    else:
        return None


@login_required()
def photo_submission_delete_view(request):
    if request.method != "POST":
        success = False
        message = "Illegal access!"
        return JsonResponse({"success": success, "message": message})

    user = request.user
    form = DeletePhotoSubmissionForm(request.POST)
    if form.is_valid():
        try:
            submission = PhotoSubmission.objects.get(user=user, id=form.cleaned_data["submission_id"])
            submission.delete()
            success = True
            message = "Submission deleted."
        except ObjectDoesNotExist:
            success = False
            message = "Submission does not exist or has been deleted. Reload the page."
    else:
        success = False
        message = "Incomplete submission, please try again."

    return JsonResponse({"success": success, "message": message})