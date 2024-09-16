from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    description = models.TextField(blank=True, null=True)
    default_location = models.CharField(max_length=200, blank=True, null=True)


class AvailabilityConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    days_availability = models.JSONField(default=list)
    initial_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    event_duration = models.DurationField()
    max_days_ahead = models.PositiveIntegerField()

    def __str__(self):
        return f"AvailabilityConfig for {self.user.username}"


class Event(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.subject
