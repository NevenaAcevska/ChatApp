from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta

from django.views.decorators.csrf import csrf_exempt

from .models import Message
from django.contrib.auth.models import User
from django.http import JsonResponse


def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")

    # Calculate the date one month ago
    one_month_ago = timezone.now() - timedelta(days=30)

    # Filter messages that are up to one month old and involve the logged-in user as either sender or recipient
    messages = Message.objects.filter(
        timestamp__gte=one_month_ago
    ).filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('timestamp')

    context = {
        'messages': messages
    }
    return render(request, "chatPage.html", context)

def user_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        q = request.GET.get('term', '')
        users = User.objects.filter(username__icontains=q)
        results = [user.username for user in users]
        return JsonResponse(results, safe=False)

