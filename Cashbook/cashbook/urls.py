from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="cashbook/auth/login.html", authentication_form=EmailLoginForm, redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("transactions/", views.transactions, name="transactions"),
    path("transactions/new/", views.transaction_create, name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.transaction_edit, name="transaction_edit"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
    path("notes/", views.notes, name="notes"),
    path("notes/new/", views.note_create, name="note_create"),
    path("notes/<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("calendar/", views.calendar, name="calendar"),
    path("calendar/new/", views.event_create, name="event_create"),
    path("calendar/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("calendar/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("calculator/", views.cash_calculator, name="calculator"),
    path("settings/", views.settings, name="settings"),
    path("settings/password/", auth_views.PasswordChangeView.as_view(template_name="cashbook/password_change.html", success_url="/settings/?password=updated"), name="password_change"),
]
