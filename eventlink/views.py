from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_date
from django.utils.timezone import now, make_aware
from django.utils.dateformat import format
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import User, Event, AvailabilityConfig
import json

MAX_EVENTS_PER_PAGE = 10  # show 10 events per page


def register_view(request):
    #  if user is authenticated, redirect to index
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirmation = request.POST.get("password_confirmation")

        # validation
        if password != password_confirmation:
            return render(
                request, "eventlink/register.html", {"message": "Passwords must match."}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "eventlink/register.html",
                {"message": "Username already taken."},
            )

        # create and save the new user
        user = User(username=username, email=email, password=make_password(password))
        user.save()

        # log the user in and redirect to the index page
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "eventlink/register.html")


def login_view(request):
    #  if user is authenticated, redirect to index
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # get form data
        username = request.POST["username"]
        password = request.POST["password"]

        # authenticate
        user = authenticate(request, username=username, password=password)

        # check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "eventlink/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "eventlink/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def index(request):
    current_datetime = now()
    events = Event.objects.filter(
        status="accepted", date_time__gte=current_datetime
    ).order_by("date_time")

    # count events happening today
    today_start = current_datetime
    today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    today_events_count = Event.objects.filter(
        status="accepted", date_time__range=(today_start, today_end)
    ).count()

    # get pending events
    pending_events = Event.objects.filter(status="pending").order_by("date_time")

    # mark events that are happening today
    for event in events:
        event.is_today = today_start <= event.date_time <= today_end

    # paginate events
    paginator = Paginator(events, MAX_EVENTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "eventlink/index.html",
        {
            "page_obj": page_obj,
            "today_events_count": today_events_count,
            "pending_count": pending_events.count(),
        },
    )


@login_required
def cancel_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        reason = request.POST.get("reason")

        if not event_id or not reason:
            return redirect("index")  # handle validation errors as needed

        event = get_object_or_404(Event, id=event_id)
        event.status = "canceled"
        event.reason = reason
        event.save()

        return redirect("index")


@login_required
def pending(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        action = request.POST.get("action")
        location = request.POST.get("location")
        reason = request.POST.get("reason")

        if event_id and action in ["accept", "reject"]:
            event = get_object_or_404(Event, id=event_id)
            if action == "accept":
                if not location:
                    return render(
                        request,
                        "eventlink/pending.html",
                        {
                            "pending_events": Event.objects.filter(
                                status="pending"
                            ).order_by("date_time"),
                            "error": "Location is required to accept the event.",
                        },
                    )
                event.status = "accepted"
                event.location = location
                event.reason = None
            elif action == "reject":
                if not reason:
                    return render(
                        request,
                        "eventlink/pending.html",
                        {
                            "pending_events": Event.objects.filter(
                                status="pending"
                            ).order_by("date_time"),
                            "error": "Reason is required to reject the event.",
                        },
                    )
                event.status = "rejected"
                event.location = None
                event.reason = reason
            event.save()
            return redirect("pending")

    # get pending events
    pending_events = Event.objects.filter(status="pending").order_by("date_time")

    # paginate events
    paginator = Paginator(pending_events, MAX_EVENTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "eventlink/pending.html",
        {
            "page_obj": page_obj,
            "pending_count": pending_events.count(),
            "default_location": request.user.default_location,
        },
    )


@login_required
def history(request):
    current_datetime = now()
    # retrieve past events and future canceled and rejected events
    past_events = Event.objects.filter(date_time__lte=current_datetime).order_by(
        "-date_time"
    )
    future_canceled_or_rejected = Event.objects.filter(
        date_time__gt=current_datetime, status__in=["canceled", "rejected"]
    ).order_by("-date_time")

    # combine and sort all events
    all_events = list(past_events) + list(future_canceled_or_rejected)
    all_events.sort(key=lambda e: e.date_time, reverse=True)

    # get pending events
    pending_events = Event.objects.filter(status="pending").order_by("date_time")

    # paginate events
    paginator = Paginator(all_events, MAX_EVENTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "eventlink/history.html",
        {
            "page_obj": page_obj,
            "pending_count": pending_events.count(),
        },
    )


@login_required
def search(request):
    # Retrieve query parameters from GET request
    query_params = {
        "subject": request.GET.get("subject", ""),
        "description": request.GET.get("description", ""),
        "date": request.GET.get("date", ""),
        "requester_name": request.GET.get("requester_name", ""),
        "requester_email": request.GET.get("requester_email", ""),
        "status": request.GET.get("status", ""),
    }

    events = Event.objects.all()
    error_message = None
    page_obj = None
    no_events_found = False

    # Check if the search form was submitted
    if "search" in request.GET:
        # Check if any search parameters are provided
        if any(query_params.values()):
            # Filtering based on query parameters
            if query_params["subject"]:
                events = events.filter(subject__icontains=query_params["subject"])
            if query_params["description"]:
                events = events.filter(
                    description__icontains=query_params["description"]
                )
            if query_params["date"]:
                # Convert the date string to a datetime object
                date_obj = parse_date(query_params["date"])
                if date_obj:
                    # Filter events based on the date part of the 'date_time' field
                    events = events.filter(date_time__date=date_obj)
            if query_params["requester_name"]:
                events = events.filter(name__icontains=query_params["requester_name"])
            if query_params["requester_email"]:
                events = events.filter(email__icontains=query_params["requester_email"])
            if query_params["status"]:
                events = events.filter(status=query_params["status"])

            # Check if no events are found
            if not events.exists():
                no_events_found = True
            else:
                # Paginate events
                paginator = Paginator(events, MAX_EVENTS_PER_PAGE)
                page_number = request.GET.get("page")
                page_obj = paginator.get_page(page_number)
        else:
            error_message = "Please provide at least one parameter."

    context = {
        "page_obj": page_obj,
        "query_params": query_params,
        "error_message": error_message,
        "no_events_found": no_events_found,
    }

    return render(request, "eventlink/search.html", context)


@login_required
def profile(request):
    user = request.user
    try:
        availability_config = AvailabilityConfig.objects.get(user=user)
    except AvailabilityConfig.DoesNotExist:
        # create a default AvailabilityConfig if it does not exist
        availability_config = AvailabilityConfig(
            user=user,
            days_availability=[],
            initial_time=None,
            end_time=None,
            event_duration=timedelta(hours=1),  # default duration
            max_days_ahead=15,  # default max days ahead
        )
        availability_config.save()

    if request.method == "POST":
        # get form data
        name = request.POST.get("name")
        description = request.POST.get("description")
        default_location = request.POST.get("default_location")
        days_availability = request.POST.getlist("days_availability")
        initial_time = request.POST.get("initial_time")
        end_time = request.POST.get("end_time")
        event_duration = request.POST.get("event_duration")
        max_days_ahead = request.POST.get("max_days_ahead")

        # check if all required fields are filled
        if not days_availability or not initial_time or not end_time:
            return render(
                request,
                "eventlink/profile.html",
                {
                    "user": user,
                    "availability_config": availability_config,
                    "error": "Please fill all the fields related to availability.",
                    "initial_time": initial_time,
                    "end_time": end_time,
                    "event_duration": event_duration,
                    "max_days_ahead": max_days_ahead,
                },
            )

        # update user profile
        user.username = name
        user.description = description
        user.default_location = default_location
        user.save()

        # update or create the AvailabilityConfig
        availability_config.days_availability = days_availability
        availability_config.initial_time = (
            datetime.strptime(initial_time, "%H:%M").time() if initial_time else None
        )
        availability_config.end_time = (
            datetime.strptime(end_time, "%H:%M").time() if end_time else None
        )
        # remove decimal part from event duratio
        if event_duration:
            availability_config.event_duration = timedelta(
                minutes=int(float(event_duration))
            )
        # save max days ahead
        if max_days_ahead:
            availability_config.max_days_ahead = int(max_days_ahead)
        availability_config.save()

        return redirect("profile")  # redirect back to the profile page

    # convert event_duration to integer minutes for display
    event_duration_minutes = (
        int(availability_config.event_duration.total_seconds() // 60)
        if availability_config.event_duration
        else ""
    )

    # get pending events
    pending_events = Event.objects.filter(status="pending").order_by("date_time")

    return render(
        request,
        "eventlink/profile.html",
        {
            "user": user,
            "availability_config": availability_config,
            "initial_time": availability_config.initial_time.strftime("%H:%M")
            if availability_config.initial_time
            else "",
            "end_time": availability_config.end_time.strftime("%H:%M")
            if availability_config.end_time
            else "",
            "event_duration": event_duration_minutes,
            "max_days_ahead": availability_config.max_days_ahead
            if availability_config.max_days_ahead
            else "",
            "pending_count": pending_events.count(),
        },
    )


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "eventlink/event_detail.html", {"event": event})


def create_event(request, user_id):
    user = get_object_or_404(User, id=user_id)
    config = get_object_or_404(AvailabilityConfig, user=user)

    if request.method == "POST":
        subject = request.POST.get("subject")
        event_date = request.POST.get("event_date")
        event_time = request.POST.get("event_time")
        event_description = request.POST.get("description")
        name = request.POST.get("name")
        email = request.POST.get("email")

        if not all([subject, event_date, event_time, name, email]):
            return render(
                request,
                "eventlink/create_event.html",
                {
                    "user": user,
                    "config": config,
                    "error": "All fields are required.",
                },
            )

        # validate and parse the datetime values
        try:
            event_date_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
            event_time_dt = datetime.strptime(event_time, "%H:%M").time()
            event_datetime = datetime.combine(event_date_dt, event_time_dt)
        except ValueError:
            return render(
                request,
                "eventlink/create_event.html",
                {
                    "user": user,
                    "config": config,
                    "error": "Invalid date or time format.",
                },
            )

        # ensure event_datetime is timezone-aware
        if event_datetime and not event_datetime.tzinfo:
            event_datetime = make_aware(event_datetime)

        current_time = now()

        # validate time is greater than current time
        if event_datetime < current_time:
            return render(
                request,
                "eventlink/create_event.html",
                {
                    "user": user,
                    "config": config,
                    "error": "Event cannot be scheduled in the past.",
                },
            )

        # validate datetime is in the config max day ahead range
        max_date = current_time + timedelta(days=config.max_days_ahead)
        if event_datetime > max_date:
            return render(
                request,
                "eventlink/create_event.html",
                {
                    "user": user,
                    "config": config,
                    "error": f"Event cannot be scheduled more than {config.max_days_ahead} days ahead.",
                },
            )

        event_day = event_datetime.strftime("%A")
        event_time = event_datetime.time()

        # validate if date is on the config day availability
        if event_day not in config.days_availability:
            return render(
                request,
                "eventlink/create_event.html",
                {
                    "user": user,
                    "config": config,
                    "error": "Selected day is not available.",
                },
            )

        # check for conflicts with existing events
        if Event.objects.filter(user=user, date_time__date=event_date_dt).exists():
            existing_events = Event.objects.filter(
                user=user,
                date_time__date=event_date_dt,
                status__in=["accepted", "pending"],
            )

            for existing_event in existing_events:
                existing_start = existing_event.date_time
                existing_end = existing_start + config.event_duration

                # ensure existing times are timezone-aware
                if existing_start and not existing_start.tzinfo:
                    existing_start = make_aware(existing_start)
                if existing_end and not existing_end.tzinfo:
                    existing_end = make_aware(existing_end)

                if (
                    existing_start.time() <= event_time <= existing_end.time()
                    or existing_start.time() <= event_time_dt <= existing_end.time()
                ):
                    return render(
                        request,
                        "eventlink/create_event.html",
                        {
                            "user": user,
                            "config": config,
                            "error": "Time slot is already taken.",
                        },
                    )

        event = Event(
            user=user,
            subject=subject,
            description=event_description,
            date_time=event_datetime,
            name=name,
            email=email,
        )
        event.save()

        # redirect to the event detail page after saving
        return redirect("event_detail", event_id=event.id)

    # TIME SLOTS
    time_slots = {}
    current_date = now().date()
    max_date = current_date + timedelta(days=config.max_days_ahead)

    # iterate over each day within the range of dates
    date = current_date
    while date <= max_date:
        # check if the current date is a day when the user is available
        if date.strftime("%A") in config.days_availability:
            # initialize slot start time for the current day
            slot_start = config.initial_time

            # generate time slots for the current day
            while True:
                # calculate the end time for the current slot
                slot_end = (
                    datetime.combine(datetime.today(), slot_start)
                    + config.event_duration
                ).time()
                # break the loop if the slot end time exceeds the configured end time
                if slot_end > config.end_time:
                    break

                # define the start and end datetime for the current slot
                slot_start_dt = datetime.combine(date, slot_start)
                slot_end_dt = datetime.combine(date, slot_end)

                # ensure slot times are timezone-aware
                if slot_start_dt and not slot_start_dt.tzinfo:
                    slot_start_dt = make_aware(slot_start_dt)
                if slot_end_dt and not slot_end_dt.tzinfo:
                    slot_end_dt = make_aware(slot_end_dt)

                # get existing events for the user on this date
                existing_events = Event.objects.filter(
                    user=user, date_time__date=date, status__in=["accepted", "pending"]
                )

                # check if the slot overlaps with any existing events
                slot_conflicted = False
                for event in existing_events:
                    event_start = event.date_time
                    event_end = event_start + config.event_duration

                    # ensure event times are timezone-aware
                    if event_start and not event_start.tzinfo:
                        event_start = make_aware(event_start)
                    if event_end and not event_end.tzinfo:
                        event_end = make_aware(event_end)

                    if event_start < slot_end_dt and event_end > slot_start_dt:
                        slot_conflicted = True
                        break

                if not slot_conflicted:
                    # add the slot start time to the time slots dictionary for the current date
                    if date.strftime("%Y-%m-%d") not in time_slots:
                        time_slots[date.strftime("%Y-%m-%d")] = []
                    time_slots[date.strftime("%Y-%m-%d")].append(
                        slot_start.strftime("%H:%M")
                    )

                # move to the next slot start time
                slot_start = (
                    datetime.combine(datetime.today(), slot_start)
                    + config.event_duration
                ).time()

        # move to the next day
        date += timedelta(days=1)

    # determine the first available day with time slots
    first_available_date = min(time_slots.keys()) if time_slots else None

    # format dates as YYYY-MM-DD for min and max attributes
    formatted_current_date = format(current_date, "Y-m-d")
    formatted_max_date = format(max_date, "Y-m-d")

    # serialize time slots to JSON
    time_slots_json = json.dumps(time_slots)

    return render(
        request,
        "eventlink/create_event.html",
        {
            "user": user,
            "config": config,
            "time_slots": time_slots_json,
            "first_available_date": first_available_date,
            "current_date": formatted_current_date,
            "max_date": formatted_max_date,
        },
    )
