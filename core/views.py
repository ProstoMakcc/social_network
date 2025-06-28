from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def homepage(request):
    context = {
        'chats': request.user.chats.all(),
    }
    return render(request, 'homepage.html', context)