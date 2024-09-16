from django.contrib import admin
from .models import User, AvailabilityConfig, Event

# Register your models here.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(AvailabilityConfig)
