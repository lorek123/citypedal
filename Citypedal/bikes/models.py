    # -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone


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

    TYPE_TOPUP = "T"
    TYPE_TRIP = "R"
    TYPE_CHAN = "C"
    TYPE_REFUND = "E"
    TYPE_PROMOTION = "P"
    TYPE_CHOICES = (
        (TYPE_TOPUP, "Wpłata"),
        (TYPE_TRIP, "Podróż"),
        (TYPE_CHAN, "Kara"),
        (TYPE_REFUND, "Zwrot"),
        (TYPE_PROMOTION, "Promocja"),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)


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

    def save(self):
        if self.station:
            self.state = Bike.STATE_BORROWED
        elif self.state != Bike.STATE_SERVICED:
            self.state = Bike.STATE_AVAILABLE
        super().save()


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
        return self.to_station is None

    @property
    def duration(self):
        if self.ended_at is None:
            raise ValueError("Trip has not ended yet")
        return self.ended_at - self.started_at

    @property
    def price(self):
        # losowo ustalona cena za pomocą rzutu kostką
        return Decimal(4)

    def save(self, *args, **kwargs):
        if self.to_station:
            self.bike.station = self.to_station
            if self.ended_at is None:
                self.ended_at = datetime.now()
        else:
            self.bike.station = None
        self.bike.save()
        super().save(*args, **kwargs)
        Transaction.objects.create(user=self.user,
                                   amount=self.price,
                                   trip=self, type=Transaction.TYPE_TRIP)
