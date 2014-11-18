from django.shortcuts import render
from django.contrib.auth import get_user_model


def home(request, **kwargs):
    return render(request, 'home.html', {})
