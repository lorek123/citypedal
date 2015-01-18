from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from bikes.forms import RegisterForm


def home(request, **kwargs):
    return render(request, 'home.html', {})

def trips(request):
    return render(request, 'trips.html', {
        'trips': request.user.trips.all()
    })

def register(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))
    register_form = RegisterForm()

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Welcome aboard, {0}.".format(user))
            return redirect(reverse('home'))

    return render(request, 'register.html', {
        'register_form': register_form,
    })

def login_view(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))
    form = AuthenticationForm(None, request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Hey there, {0}!".format(user))
        return redirect(reverse('home'))
    return render(request, 'login.html', {
        'form': form,
    })

def logout_view(request):
    logout(request)
    return redirect(reverse('home'))
