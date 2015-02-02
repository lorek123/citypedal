import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.contenttypes.models import ContentType
from paypal.standard.forms import PayPalPaymentsForm
from bikes.models import Bike, Station, Trip, Ticket
from bikes.forms import RegisterForm, DisputeForm


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


@login_required
def topup(request):
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "10.00",
        "item_name": "Doładowanie konta",
        "invoice": uuid.uuid4(),
        "notify_url": "https://citypedal.cloudapp.net" + reverse('paypal-ipn'),
        "return_url": "https://citypedal.cloudapp.net/",
        "cancel_return": "https://citypedal.cloudapp.net/",

    }

    return render(request, 'topup.html', {
        'form': PayPalPaymentsForm(initial=paypal_dict)
    })


@login_required
def dispute(request, trip_id):
    trip = get_object_or_404(request.user.trips, pk=trip_id)
    if Ticket.objects.filter(
        content_type=ContentType.objects.get_for_model(trip),
        object_id=trip.pk
    ).exists():
        messages.warning(request, "Ticket dla tej podróży już istnieje")
        return redirect(reverse('home'))
    form = DisputeForm()
    if request.method == 'POST':
        form = DisputeForm(request.POST)
        if form.is_valid():
            ticket = Ticket.objects.create(
                    content_type=ContentType.objects.get_for_model(trip),
                    object_id=trip.pk,
                    user=request.user,
                    description=form.cleaned_data['description']
                )
            messages.success(request, "Założono ticket.")
            return redirect(reverse('ticket-details', args=[str(ticket.id)]))
    return render(request, 'dispute.html', {
        'form': form
    })


@login_required
def ticket_details(request, ticket_id):
    tickets = Ticket if request.user.is_staff else request.user.tickets
    ticket = get_object_or_404(tickets, pk=ticket_id)
    return render(request, 'ticket-details.html', {
        'ticket': ticket,
    })


@login_required
def ticket_reject(request, ticket_id):
    if not request.user.is_staff:
        return redirect(reverse('home'))
    ticket = get_object_or_404(Ticket.objects.filter(resolved_at__isnull=True),
                               pk=ticket_id)
    ticket.resolve()
    ticket.save()
    messages.success(request, "Odrzucono ticket")
    return redirect(ticket.get_absolute_url())


@login_required
def ticket_refund(request, ticket_id):
    if not request.user.is_staff:
        return redirect(reverse('home'))
    ticket = get_object_or_404(Ticket.objects.filter(resolved_at__isnull=True),
                               pk=ticket_id)
    ticket.resolve(refund=True)
    ticket.save()
    messages.success(request, "Uznano ticket")
    return redirect(ticket.get_absolute_url())


@login_required
def tickets(request):
    return render(request, 'tickets.html', {
        'tickets': request.user.tickets.order_by('-resolved_at', '-id')
        })


@login_required
def tickets_admin(request):
    if not request.user.is_staff:
        return redirect(reverse('home'))
    return render(request, 'tickets-admin.html', {
        'tickets': Ticket.objects.filter(resolved_at__isnull=True)
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
