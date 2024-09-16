from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("pending/", views.pending, name="pending"),
    path("profile/", views.profile, name="profile"),
    path("booking/<int:user_id>/", views.create_event, name="create_event"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("cancel/", views.cancel_event, name="cancel_event"),
    path("history/", views.history, name="history"),
    path("search/", views.search, name="search"),
]
