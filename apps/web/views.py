from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import time

from ..tiktokinfo.tiktok_user import lookup_tiktok_user, update_tiktok_user, check_user_for_updates

DEFAULT_USERNAME = "@charlidamelio"
#DEFAULT_USERNAME = "@btsofkt"

def update_page_tiktokstats(request):
    if settings.DEBUG:
        print(f"\n\nInside update_page_tiktokstats as {request.method}")
    if request.user.is_authenticated:
        if request.method == 'POST':
            tiktok_user = request.POST.get('tkusername').strip()
            if not tiktok_user:
                tiktok_user = request.user.tiktokname
            if not tiktok_user:
                messages.error(request, "You don't have a TikTok Username assigned" +
                                "Open your Profile on the left and update.")
                return HttpResponseRedirect(reverse('web:home'))
            print(f"TikTok Username: {request.user.tiktokname}")
            user_info = lookup_tiktok_user(tiktok_user)
            if 'error' in user_info.keys():
                # Pop up a toast error here so user knows the problem.
                messages.error(request, user_info['error'])
                return HttpResponseRedirect(reverse('web:home'))
            # Next get the user stats and user feed
            user_stats, user_feed, chart_data = update_tiktok_user(tiktok_user,
                    snapshot_record=True)
            if user_feed and not 'error' in user_feed.keys():
                return render(request, 'web/app_home.html', context={
                    'active_tab': 'dashboard',
                    'page_title': _('Dashboard'),
                    'user_info': user_info,
                    'user_stats': user_stats,
                    'user_feed': user_feed,
                    'user_charts': chart_data,
                })
            else:
                # Pop up a toast error here so User knows the problem.
                if user_feed:
                    messages.error(request, f"Error in TikTok Feed: {user_feed['error']} for User={tiktok_user}")
                else:
                    messages.error(request, f"Error - Empty TikTok Feed for User={tiktok_user}")
                return render(request, 'web/app_home.html', context={
                    'active_tab': 'dashboard',
                    'page_title': _('Dashboard'),
                    'user_info': user_info,
                })
        else:
            subscription_holder = request.user
            if subscription_holder.has_active_subscription():
                tiktok_user = request.user.tiktokname
            else:
                tiktok_user = DEFAULT_USERNAME
            # tiktok_user = request.user.tiktokname
            user_info = lookup_tiktok_user(tiktok_user)
            user_stats,user_feed,chart_data = check_user_for_updates(tiktok_user)
            return render(request, 'web/app_home.html', context={
                'active_tab': 'dashboard',
                'page_title': _('Dashboard'),
                'user_info': user_info,
                'user_stats': user_stats,
                'user_feed': user_feed,
                'user_charts': chart_data,
            })
    else:
        return render(request, 'web/landing_page.html')

def home(request):
    if request.user.is_authenticated:
        subscription_holder = request.user
        if subscription_holder.has_active_subscription():
            tiktok_user = request.user.tiktokname
        else:
            tiktok_user = DEFAULT_USERNAME
        user_info = lookup_tiktok_user(tiktok_user)
        user_stats,user_feed,chart_data = check_user_for_updates(tiktok_user)
        return render(request, 'web/app_home.html', context={
            'active_tab': 'dashboard',
            'page_title': _('Dashboard'),
            'user_info': user_info,
            'user_stats': user_stats,
            'user_feed': user_feed,
            'user_charts': chart_data,
        })
    else:
        return render(request, 'web/landing_page.html')


def simulate_error(request):
    raise Exception('This is a simulated error.')
