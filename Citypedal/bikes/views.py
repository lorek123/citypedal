from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from bikes.models import Bike, Station, Trip
from bikes.forms import RegisterForm


def home(request, **kwargs):
    return render(request, 'home.html', {})


def transactions(request):
    return render(request, 'transactions.html', {
        'transactions': request.user.transactions.order_by('-created_at',
                                                           '-id')
    })


def trips(request):
    return render(request, 'trips.html', {
        'trips': request.user.trips.order_by('-started_at')
    })


@login_required
def trip_new(request):
    if request.user.balance <= 0:
        messages.error(request,
                       'Masz zbyt mało środków, aby wypożyczyć rower.')
        return redirect(reverse('home'))
    if request.method == 'POST':
        try:
            station_id = int(request.POST.get('station_id'))
            station = Station.objects.get(pk=station_id)
            bike = station.bikes.first()
        except (TypeError, ValueError):
            messages.error(request, "Nieprawidłowy numer stacji")
        except Station.DoesNotExist:
            messages.error(request, "Wybrana stacja nie istnieje")
        except Bike.DoesNotExist:
            messages.error(request, "Brak wolnych rowerów na stacji")
        else:
            messages.success(request,
                             "Pomyślnie wypożyczyłeś rower #{}."
                             .format(bike.id))
            trip = Trip.objects.create(from_station=station, bike=bike,
                                       user=request.user)
            return redirect('trip-details', trip_id=trip.id)
    return render(request, 'trip-new.html', {
        'stations': Station.objects.filter(is_active=True).select_related(),
    })


@login_required
def trip_details(request, trip_id):
    trip = get_object_or_404(request.user.trips, pk=trip_id)
    return render(request, 'trip-details.html', {
        'trip': trip,
    })


@login_required
def trip_finish(request, trip_id):
    trip = get_object_or_404(request.user.trips, pk=trip_id)
    if request.method == 'POST':
        try:
            station_id = int(request.POST.get('station_id'))
            station = Station.objects.get(pk=station_id)
        except (TypeError, ValueError):
            messages.error(request, "Nieprawidłowy numer stacji")
        except Station.DoesNotExist:
            messages.error(request, "Wybrana stacja nie istnieje")
        trip.to_station = station
        trip.save()
        messages.success(request,
                         "Pomyślnie zwróciłeś rower. Zapłaciłeś {} PLN."
                         .format(trip.price))
        return redirect('trip-details', trip_id=trip.id)

    return render(request, 'trip-finish.html', {
        'trip': trip,
        'stations': Station.objects.filter(is_active=True).select_related(),
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
