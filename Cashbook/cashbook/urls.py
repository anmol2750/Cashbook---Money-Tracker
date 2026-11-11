from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("verification-sent/", views.verification_sent, name="verification_sent"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("login/", auth_views.LoginView.as_view(template_name="cashbook/auth/login.html", authentication_form=EmailLoginForm, redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/", views.transaction_accounts, name="transaction_accounts"),
    path("accounts/switch/", views.switch_transaction_account, name="switch_transaction_account"),
    path("accounts/<int:pk>/rename/", views.transaction_account_rename, name="transaction_account_rename"),
    path("transactions/", views.transactions, name="transactions"),
    path("transactions/download/", views.transactions_download, name="transactions_download"),
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
    path("basic-calculator/", views.basic_calculator, name="basic_calculator"),
    path("calculator/", views.cash_calculator, name="calculator"),
    path("currency-converter/", views.currency_converter, name="currency_converter"),
    path("settings/", views.settings, name="settings"),
    path("settings/password/", views.CashbookPasswordChangeView.as_view(), name="password_change"),
]
