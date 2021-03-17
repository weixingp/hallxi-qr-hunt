"""hallxiqr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from hallxiqr.settings import IS_PHASE2
from qrhunt import views as main_view
from django.conf import settings


admin.site.site_header = 'Hall XI BoB Admin'
admin.site.site_title = 'Hall XI BoB'
admin.site.login = login_required(admin.site.login)

# Account and admin module
urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('account/check/', main_view.check_registered),
    path('account/profile/', main_view.user_details),
    path('account/landing/', main_view.landing_page)
]

core = [
    path('', main_view.home),
    path('intro', main_view.event_info_page),
    path('intro2', main_view.event_info_page2)
]


# Game Core URLs - Phase 1
core_phase1 = [
    path('submission/new/', main_view.photo_submission_new_page),
    path('submission/<str:submission_id>/', main_view.photo_submission_view_page),
]


# Game Core URLs - Phase 2
core_phase2 = [
    path('scan', main_view.scan_qr),
    path('inventory', main_view.inventory),
    path('lootbox', main_view.loot_box),
    path('location/<str:uuid>/', main_view.location_main),
    path('question/<str:uuid>', main_view.question_page),
    path('leaderboard', main_view.leaderboard),
    path('blocks', main_view.block_ranking),
]

urlpatterns += core
urlpatterns += core_phase1

if IS_PHASE2:
    urlpatterns += core_phase2

# Game actions api
actions = [
    path('action/assign-question', main_view.assign_question),
    path('action/answer-question', main_view.answer_question),
    path('action/get-blocks-stats', main_view.get_blocks_stats),
    path('action/use-item', main_view.use_item),
    path('action/open-lootbox', main_view.open_loot_box_view),
    path('action/vote', main_view.vote_view),
    path('action/comment', main_view.comment_view),
    path('action/delete-comment', main_view.comment_delete_view),
    path('action/delete-photo-submission', main_view.photo_submission_delete_view),
]
urlpatterns += actions

# Development media root setting
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
