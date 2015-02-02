# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.urlresolvers import reverse
from django.utils import timezone
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, level, **extra_fields):
        # TODO popraw integrityerrory pls
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          level=level, last_login=now,
                          joined_at=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password,
                                 self.model.LEVEL_USER, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password,
                                 self.model.LEVEL_ADMIN,
                                 is_superuser=True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=7, decimal_places=2,
                                  default=Decimal('0.00'))

    LEVEL_USER = 1
    LEVEL_SERVICE = 3
    LEVEL_SUPPORT = 6
    LEVEL_ADMIN = 9
    LEVEL_CHOICES = (
        (LEVEL_USER, "Użytkownik"),
        (LEVEL_SERVICE, "Serwisant"),
        (LEVEL_SUPPORT, "Wsparcie"),
        (LEVEL_ADMIN, "Gandalf")
    )
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES,
                                             default=LEVEL_USER)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = UserManager()

    def topup(self, amount):
        Transaction.objects.create(user=self, amount=amount,
                                   type=Transaction.TYPE_TOPUP)

    @property
    def is_staff(self):
        return self.level >= User.LEVEL_SUPPORT

    def get_short_name(self):
        return self.username


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="transactions")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    trip = models.ForeignKey("Trip", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    TYPE_TOPUP = "T"
    TYPE_TRIP = "R"
    TYPE_CHAN = "C"
    TYPE_REFUND = "E"
    TYPE_PROMOTION = "P"
    TYPE_CHOICES = (
        (TYPE_TOPUP, "Wpłata"),
        (TYPE_TRIP, "Podróż"),
        (TYPE_CHAN, "Kara"),  # #pdk
        (TYPE_REFUND, "Zwrot"),
        (TYPE_PROMOTION, "Promocja"),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def save(self, **kwargs):
        self.user.balance += self.amount
        self.user.save()
        super().save(**kwargs)


class Bike(models.Model):
    STATE_AVAILABLE = "A"
    STATE_SERVICED = "S"
    STATE_BORROWED = "B"
    STATE_CHOICES = (
        (STATE_AVAILABLE, "Dostępny"),
        (STATE_SERVICED, "W serwisie"),
        (STATE_BORROWED, "Wypożyczony"),
    )
    state = models.CharField(max_length=1, choices=STATE_CHOICES,
                             default=STATE_AVAILABLE)
    station = models.ForeignKey('Station', related_name="bikes",
                                null=True, blank=True)

    def __str__(self):
        return "Bike #{}, {}, {}".format(self.id, self.get_state_display(),
                                         self.station)

    def save(self, **kwargs):
        if not self.station:
            self.state = Bike.STATE_BORROWED
        elif self.state == Bike.STATE_BORROWED:
            self.state = Bike.STATE_AVAILABLE
        super().save(**kwargs)


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    bike = models.ForeignKey(Bike, related_name="services")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()


class Ticket(models.Model):
    limit = models.Q(app_label='bikes', model='transaction') | \
        models.Q(app_label='bikes', model='bike')
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=limit,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tickets")

    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, editable=False)

    def get_absolute_url(self):
        return reverse('ticket-details', args=[str(self.id)])

    def is_resolved(self):
        return self.resolved_at is not None
    is_resolved.boolean = True

    def resolve(self, refund=False):
        self.resolved_at = timezone.now()
        if refund and self.content_type.model == 'trip':
            Transaction.objects.create(user=self.user,
                                       amount=self.content_object.price,
                                       type=Transaction.TYPE_REFUND)


class Trip(models.Model):
    from_station = models.ForeignKey(Station, related_name="beginning_trips")
    to_station = models.ForeignKey(Station, related_name="ending_trips",
                                   null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="trips")
    bike = models.ForeignKey(Bike, related_name="trips")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_completed(self):
        return self.to_station is not None

    @property
    def duration(self):
        if self.ended_at is None:
            raise ValueError
        return self.ended_at - self.started_at

    @property
    def price(self):
        AMOUNT_PER_HOUR = Decimal('2.00')
        ended_at = self.ended_at or timezone.now()
        hours = (ended_at - self.started_at).total_seconds()/3600
        return round(AMOUNT_PER_HOUR * Decimal(hours), 2)

    def get_absolute_url(self):
        return reverse('trip-details', args=[str(self.id)])

    def __str__(self):
        return "Trip #{}".format(self.pk)

    def save(self, **kwargs):
        if self.to_station and self.ended_at is None:
            self.ended_at = timezone.now()
            Transaction.objects.create(user=self.user,
                                       amount=-self.price,
                                       trip=self, type=Transaction.TYPE_TRIP)
            self.bike.station = self.to_station
            self.bike.save()
        super().save(**kwargs)


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        Transaction.objects.create(user=User.objects.get(username='test'),
                                   amount=Decimal('10.00'))
    else:
        pass

valid_ipn_received.connect(show_me_the_money)
