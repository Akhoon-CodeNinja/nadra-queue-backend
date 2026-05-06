# accounts/urls.py

from django.urls import path
from . import views


urlpatterns = [

    # ==================================================
    # USER APIs
    # ==================================================
    path(
        'register/',
        views.register_user,
        name='register'
    ),

    path(
        'login/',
        views.login_user,
        name='login'
    ),

    path(
        'profile/<int:user_id>/',
        views.user_profile,
        name='profile'
    ),

    # ==================================================
    # FORGOT PASSWORD API
    # ==================================================
    path(
        'forgot-password/',
        views.forgot_password,
        name='forgot_password'
    ),

    # ==================================================
    # OFFICE APIs
    # ==================================================
    path(
        'offices/',
        views.office_list,
        name='offices'
    ),

    path(
        'offices/<int:office_id>/',
        views.office_detail,
        name='office_detail'
    ),

    # ==================================================
    # TOKEN APIs
    # ==================================================
    path(
        'tokens/',
        views.token_list,
        name='tokens'
    ),

    path(
        'tokens/create/',
        views.create_token,
        name='create_token'
    ),

    path(
        'my-tokens/<int:user_id>/',
        views.user_tokens,
        name='my_tokens'
    ),

    path(
        'token/<int:token_id>/cancel/',
        views.cancel_token,
        name='cancel_token'
    ),

    # ==================================================
    # DOCUMENT GUIDE AI API
    # ==================================================
    path(
        'document-guide/',
        views.document_guide,
        name='document_guide'
    ),

    # ==================================================
    # LOCATION APIs
    # ==================================================
    path(
        'cities/',
        views.city_list,
        name='cities'
    ),

    path(
        'districts/',
        views.district_list,
        name='districts'
    ),

    # ==================================================
    # CROWD DETECTION APIs  ← NEW
    # ==================================================

    # Called by live_people_counter.py every N seconds
    path(
        'crowd/detect/',
        views.crowd_detect,
        name='crowd_detect'
    ),

    # Flutter polls this for a single office live badge
    path(
        'crowd/latest/<int:office_id>/',
        views.crowd_latest,
        name='crowd_latest'
    ),

    # Optional: analytics / chart history (last 20 snapshots)
    path(
        'crowd/history/<int:office_id>/',
        views.crowd_history,
        name='crowd_history'
    ),
]