import calendar as month_calendar
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from .forms import CalendarEventForm, CurrencyFormatForm, DarkModeForm, LanguageForm, NoteForm, ProfileForm, SignUpForm, TimeFormatForm, TransactionForm
from .models import CalendarEvent, Note, Transaction

CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "AUD": "A$"}
CASH_DENOMINATIONS = {
    "INR": ["500", "200", "100", "50", "20", "10", "5", "2", "1"],
    "USD": ["100", "50", "20", "10", "5", "2", "1", "0.50", "0.25", "0.10", "0.05", "0.01"],
    "EUR": ["200", "100", "50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"],
    "GBP": ["50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"],
    "CAD": ["100", "50", "20", "10", "5", "2", "1", "0.25", "0.10", "0.05", "0.01"],
    "AUD": ["100", "50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05"],
}

def money(user, amount):
    return f"{currency_prefix(user)}{amount:,.2f}"

def currency_prefix(user):
    if user.currency_format == "code":
        return f"{user.currency} "
    return CURRENCY_SYMBOLS.get(user.currency, user.currency + " ")

def totals(queryset):
    incoming = queryset.filter(kind=Transaction.INCOME).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    outgoing = queryset.filter(kind=Transaction.EXPENSE).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return incoming, outgoing

def page_context(request, **context):
    context["currency_prefix"] = currency_prefix(request.user)
    context["time_display_format"] = "H:i" if request.user.time_format == "24h" else "g:i A"
    return context

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _("Your account is ready. Let’s get your cashbook started."))
        return redirect("dashboard")
    return render(request, "cashbook/auth/signup.html", {"form": form})

@login_required
def dashboard(request):
    today = timezone.localdate()
    all_items = Transaction.objects.filter(user=request.user)
    month_items = all_items.filter(date__year=today.year, date__month=today.month)
    month_in, month_out = totals(month_items)
    total_in, total_out = totals(all_items)
    chart = []
    for offset in range(5, -1, -1):
        month_num = today.month - offset
        year = today.year
        while month_num <= 0:
            month_num += 12
            year -= 1
        month_date = date(year, month_num, 1)
        incoming, outgoing = totals(all_items.filter(date__year=year, date__month=month_num))
        chart.append({"label": date_format(month_date, "M"), "income": float(incoming), "expense": float(outgoing)})
    max_value = max((max(item["income"], item["expense"]) for item in chart), default=0) or 1
    for item in chart:
        item["income_height"] = max(4, round(item["income"] / max_value * 100))
        item["expense_height"] = max(4, round(item["expense"] / max_value * 100))
    context = page_context(request,
        today=today, balance=money(request.user, total_in - total_out),
        month_income=money(request.user, month_in), month_expense=money(request.user, month_out),
        recent_transactions=all_items[:6], chart=chart,
        upcoming_events=CalendarEvent.objects.filter(user=request.user, date__gte=today).order_by("date", "time")[:3],
    )
    return render(request, "cashbook/dashboard.html", context)

@login_required
def transactions(request):
    items = Transaction.objects.filter(user=request.user)
    search = request.GET.get("q", "").strip()
    kind = request.GET.get("type", "")
    period = request.GET.get("period", "")
    if search:
        items = items.filter(Q(description__icontains=search) | Q(category__icontains=search))
    if kind in (Transaction.INCOME, Transaction.EXPENSE):
        items = items.filter(kind=kind)
    today = timezone.localdate()
    if period == "daily":
        items = items.filter(date=today)
    elif period == "weekly":
        week_start = today - timedelta(days=today.weekday())
        items = items.filter(date__gte=week_start, date__lt=week_start + timedelta(days=7))
    elif period == "monthly":
        items = items.filter(date__year=today.year, date__month=today.month)
    elif period == "yearly":
        items = items.filter(date__year=today.year)
    incoming, outgoing = totals(items)
    return render(request, "cashbook/transactions.html", page_context(request,
        transactions=items, search=search, kind=kind, period=period,
        total_in=money(request.user, incoming), total_out=money(request.user, outgoing),
    ))

@login_required
def transaction_create(request):
    form = TransactionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        messages.success(request, _("Transaction added to your cashbook."))
        return redirect("transactions")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="Add transaction", eyebrow="Your money", submit_label="Save transaction", cancel_url=reverse("transactions")))

@login_required
def transaction_edit(request, pk):
    item = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Transaction updated."))
        return redirect("transactions")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="Edit transaction", eyebrow="Your money", submit_label="Save changes", cancel_url=reverse("transactions")))

@login_required
def transaction_delete(request, pk):
    item = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Transaction deleted."))
        return redirect("transactions")
    return render(request, "cashbook/confirm_delete.html", page_context(request, title="Delete transaction?", object_label=str(item), cancel_url=reverse("transactions")))

@login_required
def notes(request):
    return render(request, "cashbook/notes.html", page_context(request, notes=Note.objects.filter(user=request.user)))

@login_required
def note_create(request):
    form = NoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.user = request.user
        note.save()
        messages.success(request, _("Note saved."))
        return redirect("notes")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="New note", eyebrow="Your notes", submit_label="Save note", cancel_url=reverse("notes")))

@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    form = NoteForm(request.POST or None, instance=note)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Note updated."))
        return redirect("notes")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="Edit note", eyebrow="Your notes", submit_label="Save changes", cancel_url=reverse("notes")))

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        messages.success(request, _("Note deleted."))
        return redirect("notes")
    return render(request, "cashbook/confirm_delete.html", page_context(request, title="Delete note?", object_label=note.title, cancel_url=reverse("notes")))

def calendar_grid(user, year, month):
    today = timezone.localdate()
    event_map = {}
    for event in CalendarEvent.objects.filter(user=user, date__year=year, date__month=month):
        event_map.setdefault(event.date, []).append(event)
    return [[{"date": day, "in_month": day.month == month, "is_today": day == today, "events": event_map.get(day, [])}
             for day in week] for week in month_calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)]

@login_required
def calendar(request):
    today = timezone.localdate()
    try:
        year, month = int(request.GET.get("year", today.year)), int(request.GET.get("month", today.month))
        if month < 1 or month > 12 or year < 1900 or year > 9998:
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month
    current = date(year, month, 1)
    previous = (current - timedelta(days=1)).replace(day=1)
    following = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
    return render(request, "cashbook/calendar.html", page_context(request,
        month_name=date_format(current, "F Y"), weeks=calendar_grid(request.user, year, month),
        events=CalendarEvent.objects.filter(user=request.user, date__year=year, date__month=month),
        previous_month=previous, next_month=following, today=today,
    ))

@login_required
def event_create(request):
    initial_date = timezone.localdate()
    if request.method == "GET" and request.GET.get("date"):
        try:
            initial_date = date.fromisoformat(request.GET["date"])
        except ValueError:
            pass
    form = CalendarEventForm(request.POST or None, initial={"date": initial_date})
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.user = request.user
        event.save()
        messages.success(request, _("Event added to your calendar."))
        return redirect("calendar")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="Add calendar event", eyebrow="Your calendar", submit_label="Save event", cancel_url=reverse("calendar")))

@login_required
def event_edit(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk, user=request.user)
    form = CalendarEventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Event updated."))
        return redirect("calendar")
    return render(request, "cashbook/form_page.html", page_context(request, form=form, title="Edit calendar event", eyebrow="Your calendar", submit_label="Save changes", cancel_url=reverse("calendar")))

@login_required
def event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk, user=request.user)
    if request.method == "POST":
        event.delete()
        messages.success(request, _("Event deleted."))
        return redirect("calendar")
    return render(request, "cashbook/confirm_delete.html", page_context(request, title="Delete event?", object_label=event.title, cancel_url=reverse("calendar")))

@login_required
def cash_calculator(request):
    denominations = CASH_DENOMINATIONS.get(request.user.currency, CASH_DENOMINATIONS["INR"])
    return render(request, "cashbook/calculator.html", page_context(
        request,
        denominations=[{"value": value} for value in denominations],
    ))

@login_required
def settings(request):
    action = request.POST.get("action", "") if request.method == "POST" else ""
    selected_tab = request.GET.get("tab", "")
    tab_names = {"dark_mode": "dark-mode", "language": "language", "time_format": "time-format", "currency_format": "currency-format"}
    valid_tabs = {"profile", "dark-mode", "language", "time-format", "currency-format"}
    tab = tab_names.get(action, selected_tab if selected_tab in valid_tabs else "profile")
    form = ProfileForm(request.POST if request.method == "POST" and action == "profile" else None, instance=request.user)
    language_form = LanguageForm(request.POST if action == "language" else None, instance=request.user)
    dark_mode_form = DarkModeForm(request.POST if action == "dark_mode" else None, instance=request.user)
    time_format_form = TimeFormatForm(request.POST if action == "time_format" else None, instance=request.user)
    currency_format_form = CurrencyFormatForm(request.POST if action == "currency_format" else None, instance=request.user)
    if request.method == "POST" and action == "language" and language_form.is_valid():
        language_form.save()
        messages.success(request, _("Your language preference has been saved."))
        return redirect("/settings/?tab=language")
    if request.method == "POST" and action == "dark_mode" and dark_mode_form.is_valid():
        dark_mode_form.save()
        messages.success(request, _("Your appearance preference has been saved."))
        return redirect("/settings/?tab=dark-mode")
    if request.method == "POST" and action == "time_format" and time_format_form.is_valid():
        time_format_form.save()
        messages.success(request, _("Your time format preference has been saved."))
        return redirect("/settings/?tab=time-format")
    if request.method == "POST" and action == "currency_format" and currency_format_form.is_valid():
        currency_format_form.save()
        messages.success(request, _("Your currency format preference has been saved."))
        return redirect("/settings/?tab=currency-format")
    if request.method == "POST" and action == "profile" and form.is_valid():
        form.save()
        messages.success(request, _("Your profile settings are saved."))
        return redirect("settings")
    return render(request, "cashbook/settings.html", page_context(
        request, form=form, language_form=language_form, dark_mode_form=dark_mode_form,
        time_format_form=time_format_form, currency_format_form=currency_format_form, tab=tab,
    ))
