from .models import Location, AssignedLocation, Question, AssignedQuestion, User, AssignedLootBox, Profile, PointsRecord
from .models import Block, HpLog, AssignedItem, Item

from django.utils.timezone import localtime, now
from random import randint
from django.db.models import Avg, Count, Min, Sum
from random import random


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

    return new_question.uuid


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
    # Check if such difficulty question exist
    count = Question.objects.filter(difficulty=difficulty).count()
    if count < 1:
        return None

    # Get answered/assigned questions of user.
    answered_question = AssignedQuestion.objects \
        .filter(user=user, question__isnull=False) \
        .values_list('question_id', flat=True)

    # Exclude the questions that have been answered.
    pks = Question.objects.filter(difficulty=difficulty) \
        .exclude(id__in=list(answered_question)) \
        .values_list('pk', flat=True, )

    if len(pks) < 1:
        pks = Question.objects.filter(difficulty=difficulty).values_list('pk', flat=True, )

    # Get random question of the processed list of questions
    random_idx = randint(0, len(pks) - 1)
    random_qn = Question.objects.get(pk=pks[random_idx])

    return random_qn


def assign_loot_box(user, amount):
    pass


def get_block_hp(block):
    max_hp = block.max_hp
    value = HpLog.objects.filter(target_block=block).aggregate(Sum('value'))
    value = value["value__sum"]
    if not value:
        value = 0
    curr_hp = max_hp + value
    if curr_hp < 0:
        curr_hp = 0

    if curr_hp > max_hp:
        curr_hp = max_hp

    return [curr_hp, max_hp]


def get_block_exploration(block):
    max_exploration = block.max_exploration_points
    curr_exploration = AssignedLocation.objects \
        .filter(user__profile__block=block, has_visited=True) \
        .aggregate(Sum('id'))
    curr_exploration = curr_exploration["id__sum"]

    if not curr_exploration:
        curr_exploration = 0

    return [curr_exploration, max_exploration]


def use_item(user, item, block):
    hp = None
    if item.user != user:
        success = False
        message = "This item does not belong to you. Are you logged in to the right account?"
    elif item.has_used:
        success = False
        message = "This item has been used."
    else:
        if item.item.type == "1":
            # Attack item
            value = -item.item.value
            message = "You dealt " + str(item.item.value) + " damage to block " + block.name + "."
        elif item.item.type == "2":
            value = item.item.value
            message = "You healed " + str(item.item.value) + " HP to block " + block.name + "."
        else:
            success = False
            message = "This item can't be used."
            return {
                "success": success,
                "message": message,
            }

        # Save the HP Log
        HpLog.objects.create(
            user=user,
            target_block=block,
            value=value,
            reason="Used item id " + str(item.item.id)
        )
        item.has_used = True
        item.time_used = localtime(now())
        item.save()

        # Add points for using the item
        PointsRecord.objects.create(
            user=user,
            points_change=item.get_points(),
            reason=f"Using assigned item id: {item.id}",
        )

        hp = get_block_hp(block)
        success = True
    return {"success": success, "message": message, "hp": hp}


def open_loot_box(box):
    rand = random()

    if rand < 0.6:
        # Common
        rarity = "1"
    elif rand < 0.91:
        # Rare
        rarity = "2"
    elif rand < 0.99:
        # Super Rare
        rarity = "3"
    else:
        # Legendary
        rarity = "4"

    pks = Item.objects.filter(rarity=rarity).values_list('pk', flat=True, )
    if not pks:
        pks = Item.objects.filter().values_list('pk', flat=True, )

    random_idx = randint(0, len(pks) - 1)
    random_item = Item.objects.get(pk=pks[random_idx])

    new_item = AssignedItem.objects.create(
        user=box.user,
        item=random_item,
    )

    box.has_opened = True
    box.assigned_item = new_item
    box.time_opened = localtime(now())
    box.save()

    return random_item


def get_total_blk_player(block):
    player_count = Profile.objects.filter(block=block).count()
    return player_count


def get_unanswered_qn(user):
    question_list = AssignedQuestion.objects.filter(
        user=user,
        has_answered=False,
        time__date=localtime(now()).date(),
    )
    res = []
    for question in question_list:
        temp = {
            "uuid": question.uuid,
            "question": str(question.question)
        }
        res.append(temp)

    return res


def get_user_points(user):
    points = PointsRecord.objects.filter(user=user).aggregate(Sum('points_change'))
    print(points)
    user_points = points['points_change__sum']
    if not user_points:
        user_points = 0
    return user_points


def get_leaderboard():
    leaderboard = PointsRecord.objects.all()\
        .values('user')\
        .annotate(total_points=Sum('points_change'))\
        .order_by('-points_change')

    profiles = Profile.objects.all()

    rank = 1
    leaderboard = list(leaderboard)

    for item in leaderboard:
        item['profile'] = profiles.get(user__id=item['user'])
        profiles = profiles.exclude(user__id=item['user'])
        item['rank'] = rank
        rank += 1

    for unranked in profiles:
        temp = {
            "user": unranked.user.id,
            "profile": unranked,
            "total_points": 0,
            "rank": rank
        }
        leaderboard.append(temp)
        rank += 1

    print(leaderboard)
    return leaderboard


def get_rank_bonus():
    bonus = [
        100,
        50,
        30,
        0
    ]
    return bonus


def get_block_ranking():
    blocks = Block.objects.all()
    bonus = get_rank_bonus()

    ranks_prop = [
        {
            "rank": 1,
            "sup": "st",
            "bonus": bonus[0],
            "color": "info"
        },
        {
            "rank": 2,
            "sup": "nd",
            "bonus": bonus[1],
            "color": "success"
        },
        {
            "rank": 3,
            "sup": "rd",
            "bonus": bonus[2],
            "color": "warning",
        },
        {
            "rank": 4,
            "sup": "th",
            "bonus": bonus[3],
            "color": "dark"
        },

    ]

    if len(ranks_prop) < len(blocks):
        raise ValueError("Rank prop size does not fit with number of blocks")

    ranks = []
    for block in blocks:
        hp = get_block_hp(block)
        exp = get_block_exploration(block)
        hp_points = round((hp[0]/hp[1])*5000)
        exp_points = round((exp[0]/exp[1])*5000)

        total_points = hp_points + exp_points
        temp = {
            "block": block.name,
            "points": total_points,
            "hp": hp,
            "exp": exp,
        }
        ranks.append(temp)

    ranks = sorted(ranks, key=lambda i: i['points'], reverse=True)

    index = 0
    for block in ranks:
        block['prop'] = ranks_prop[index]
        index += 1

    return ranks
