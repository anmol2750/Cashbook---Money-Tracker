import calendar as month_calendar
import logging
import secrets
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.conf import settings as django_settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from .forms import CalendarEventForm, CurrencyFormatForm, DarkModeForm, DateFormatForm, LanguageForm, NoteForm, ProfileForm, SignUpForm, TimeFormatForm, TransactionAccountForm, TransactionAccountNameForm, TransactionForm, VerificationOTPForm, VerificationResendForm
from .models import CalendarEvent, EmailVerificationCode, Note, Transaction, TransactionAccount, User

CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "AUD": "A$"}
CASH_DENOMINATIONS = {
    "INR": ["500", "200", "100", "50", "20", "10", "5", "2", "1"],
    "USD": ["100", "50", "20", "10", "5", "2", "1", "0.50", "0.25", "0.10", "0.05", "0.01"],
    "EUR": ["200", "100", "50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"],
    "GBP": ["50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"],
    "CAD": ["100", "50", "20", "10", "5", "2", "1", "0.25", "0.10", "0.05", "0.01"],
    "AUD": ["100", "50", "20", "10", "5", "2", "1", "0.50", "0.20", "0.10", "0.05"],
}
DATE_DISPLAY_FORMATS = {"dmy": "d/m/Y", "mdy": "m/d/Y", "ymd": "Y-m-d"}
PYTHON_DATE_FORMATS = {"dmy": "%d/%m/%Y", "mdy": "%m/%d/%Y", "ymd": "%Y-%m-%d"}
ACTIVE_ACCOUNT_SESSION_KEY = "active_transaction_account_id"
PENDING_VERIFICATION_EMAIL_SESSION_KEY = "pending_verification_email"
VERIFICATION_DELIVERY_STATUS_SESSION_KEY = "verification_delivery_status"
logger = logging.getLogger(__name__)

def money(user, amount, account=None):
    return f"{currency_prefix(user, account=account)}{amount:,.2f}"

def currency_prefix(user, account=None):
    currency = account.currency if account else user.currency
    if user.currency_format == "code":
        return f"{currency} "
    return CURRENCY_SYMBOLS.get(currency, currency + " ")

def totals(queryset):
    incoming = queryset.filter(kind=Transaction.INCOME).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    outgoing = queryset.filter(kind=Transaction.EXPENSE).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return incoming, outgoing

def get_active_account(request):
    cached_account = getattr(request, "active_transaction_account", None)
    if cached_account is not None:
        return cached_account

    accounts = TransactionAccount.objects.filter(user=request.user)
    active_account = None
    session_account_id = request.session.get(ACTIVE_ACCOUNT_SESSION_KEY)
    if session_account_id:
        active_account = accounts.filter(pk=session_account_id).first()
    if active_account is None:
        active_account = accounts.filter(is_default=True).first() or accounts.first()
    if active_account is None:
        active_account, _ = TransactionAccount.objects.get_or_create(
            user=request.user,
            name="Cash",
            defaults={"currency": request.user.currency, "is_default": True},
        )

    request.session[ACTIVE_ACCOUNT_SESSION_KEY] = active_account.pk
    request.active_transaction_account = active_account
    return active_account

def page_context(request, **context):
    active_account = context.get("active_account") or get_active_account(request)
    accounts = context.get("accounts")
    if accounts is None:
        accounts = list(TransactionAccount.objects.filter(user=request.user))
    context["active_account"] = active_account
    context["accounts"] = accounts
    context["currency_prefix"] = currency_prefix(request.user, account=active_account)
    context["transaction_currency"] = active_account.currency
    context["date_display_format"] = DATE_DISPLAY_FORMATS.get(request.user.date_format, "d/m/Y")
    context["time_display_format"] = "H:i" if request.user.time_format == "24h" else "g:i A"
    return context

def send_verification_otp(user):
    code = f"{secrets.randbelow(1_000_000):06d}"
    now = timezone.now()
    verification, created = EmailVerificationCode.objects.get_or_create(
        user=user,
        defaults={
            "code_hash": make_password(code),
            "expires_at": now + timedelta(seconds=django_settings.EMAIL_VERIFICATION_OTP_TTL_SECONDS),
            "last_sent_at": now,
        },
    )
    if not created:
        verification.code_hash = make_password(code)
        verification.expires_at = now + timedelta(seconds=django_settings.EMAIL_VERIFICATION_OTP_TTL_SECONDS)
        verification.attempts = 0
        verification.last_sent_at = now
        verification.save(update_fields=["code_hash", "expires_at", "attempts", "last_sent_at"])
    body = render_to_string("cashbook/auth/verification_email.txt", {
        "user": user,
        "code": code,
        "expires_minutes": max(1, (django_settings.EMAIL_VERIFICATION_OTP_TTL_SECONDS + 59) // 60),
    })
    try:
        sent_count = send_mail(
            subject=str(_("Your Cashbook verification code")),
            message=body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Could not send an email verification code to user %s", user.pk)
        verification.last_sent_at = timezone.now() - timedelta(
            seconds=django_settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS
        )
        verification.save(update_fields=["last_sent_at"])
        return False
    if sent_count <= 0:
        verification.last_sent_at = timezone.now() - timedelta(
            seconds=django_settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS
        )
        verification.save(update_fields=["last_sent_at"])
        return False
    return True

class CashbookPasswordChangeView(PasswordChangeView):
    template_name = "cashbook/password_change.html"
    success_url = "/settings/?password=updated"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(page_context(self.request))
        return context

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        account = TransactionAccount.objects.create(
            user=user, name="Cash", currency=user.currency, is_default=True,
        )
        request.session[ACTIVE_ACCOUNT_SESSION_KEY] = account.pk
        request.session[PENDING_VERIFICATION_EMAIL_SESSION_KEY] = user.email
        email_sent = send_verification_otp(user)
        request.session[VERIFICATION_DELIVERY_STATUS_SESSION_KEY] = "sent" if email_sent else "failed"
        return redirect("verification_sent")
    return render(request, "cashbook/auth/signup.html", {"form": form})

def verification_sent(request):
    email = request.session.get(PENDING_VERIFICATION_EMAIL_SESSION_KEY, "")
    delivery_status = request.session.pop(VERIFICATION_DELIVERY_STATUS_SESSION_KEY, "generic")
    form = VerificationOTPForm(initial={"email": email})
    return render(request, "cashbook/auth/verification_sent.html", {
        "email": email,
        "delivery_status": delivery_status,
        "form": form,
        "expires_minutes": max(1, (django_settings.EMAIL_VERIFICATION_OTP_TTL_SECONDS + 59) // 60),
        "console_backend": django_settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend",
    })

def resend_verification(request):
    form = VerificationResendForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.filter(email__iexact=email, is_active=False).first()
        if user:
            verification = EmailVerificationCode.objects.filter(user=user).first()
            cooldown = timedelta(seconds=django_settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS)
            if verification is None or timezone.now() - verification.last_sent_at >= cooldown:
                send_verification_otp(user)
        request.session[PENDING_VERIFICATION_EMAIL_SESSION_KEY] = email
        request.session[VERIFICATION_DELIVERY_STATUS_SESSION_KEY] = "requested"
        return redirect("verification_sent")
    return render(request, "cashbook/auth/resend_verification.html", {"form": form})

def verify_otp(request):
    email = request.session.get(PENDING_VERIFICATION_EMAIL_SESSION_KEY, "")
    form = VerificationOTPForm(request.POST or None, initial={"email": email})
    if request.method == "POST" and form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data["email"], is_active=False).first()
        verification = EmailVerificationCode.objects.filter(user=user).first() if user else None
        if verification is None:
            form.add_error(None, _("The email or verification code is invalid."))
        elif timezone.now() >= verification.expires_at:
            verification.delete()
            form.add_error("code", _("This code has expired. Request a new code to continue."))
        elif verification.attempts >= django_settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
            form.add_error("code", _("Too many incorrect attempts. Request a new code to continue."))
        elif check_password(form.cleaned_data["code"], verification.code_hash):
            user.is_active = True
            user.save(update_fields=["is_active"])
            verification.delete()
            request.session.pop(PENDING_VERIFICATION_EMAIL_SESSION_KEY, None)
            request.session.pop(VERIFICATION_DELIVERY_STATUS_SESSION_KEY, None)
            return render(request, "cashbook/auth/verification_success.html")
        else:
            verification.attempts += 1
            verification.save(update_fields=["attempts"])
            if verification.attempts >= django_settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
                form.add_error("code", _("Too many incorrect attempts. Request a new code to continue."))
            else:
                form.add_error("code", _("That code is incorrect. Check your email and try again."))

    return render(request, "cashbook/auth/verification_sent.html", {
        "email": form["email"].value() or email,
        "delivery_status": request.session.get(VERIFICATION_DELIVERY_STATUS_SESSION_KEY, "generic"),
        "form": form,
        "expires_minutes": max(1, (django_settings.EMAIL_VERIFICATION_OTP_TTL_SECONDS + 59) // 60),
        "console_backend": django_settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend",
    })

@login_required
@require_POST
def switch_transaction_account(request):
    account = get_object_or_404(
        TransactionAccount,
        pk=request.POST.get("account_id"),
        user=request.user,
    )
    request.session[ACTIVE_ACCOUNT_SESSION_KEY] = account.pk
    request.active_transaction_account = account
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("dashboard")
    return redirect(next_url)

@login_required
def transaction_accounts(request):
    active_account = get_active_account(request)
    form = TransactionAccountForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        account = form.save(commit=False)
        account.user = request.user
        account.save()
        request.session[ACTIVE_ACCOUNT_SESSION_KEY] = account.pk
        request.active_transaction_account = account
        messages.success(request, _("Transaction account created."))
        return redirect("transaction_accounts")

    accounts = list(TransactionAccount.objects.filter(user=request.user))
    account_summaries = []
    for account in accounts:
        account_in, account_out = totals(Transaction.objects.filter(user=request.user, account=account))
        account_summaries.append({
            "account": account,
            "balance": money(request.user, account_in - account_out, account=account),
            "transaction_count": account.transactions.count(),
            "is_active": account.pk == active_account.pk,
        })
    return render(request, "cashbook/accounts.html", page_context(
        request, form=form, account_summaries=account_summaries,
        accounts=accounts, active_account=active_account,
    ))

@login_required
def transaction_account_rename(request, pk):
    account = get_object_or_404(TransactionAccount, pk=pk, user=request.user)
    form = TransactionAccountNameForm(request.POST or None, instance=account, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Account name updated."))
        return redirect("transaction_accounts")
    return render(request, "cashbook/form_page.html", page_context(
        request,
        form=form,
        title="Rename account",
        eyebrow="Your money",
        submit_label="Save account name",
        cancel_url=reverse("transaction_accounts"),
    ))

@login_required
def dashboard(request):
    account = get_active_account(request)
    today = timezone.localdate()
    all_items = Transaction.objects.filter(user=request.user, account=account)
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
        today=today, balance=money(request.user, total_in - total_out, account=account),
        month_income=money(request.user, month_in, account=account), month_expense=money(request.user, month_out, account=account),
        active_account=account,
        recent_transactions=all_items[:6], chart=chart,
        upcoming_events=CalendarEvent.objects.filter(user=request.user, date__gte=today).order_by("date", "time")[:3],
    )
    return render(request, "cashbook/dashboard.html", context)

def filtered_transactions(request):
    account = get_active_account(request)
    user_items = Transaction.objects.filter(user=request.user, account=account)
    categories = list(
        user_items.exclude(category="")
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )
    items = user_items
    search = request.GET.get("q", "").strip()
    kind = request.GET.get("type", "")
    period = request.GET.get("period", "")
    category = request.GET.get("category", "").strip()
    if search:
        items = items.filter(Q(description__icontains=search) | Q(category__icontains=search))
    if kind in (Transaction.INCOME, Transaction.EXPENSE):
        items = items.filter(kind=kind)
    if category in categories:
        items = items.filter(category=category)
    else:
        category = ""
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
    return items, categories, {
        "search": search,
        "kind": kind,
        "period": period,
        "category": category,
    }

@login_required
def transactions(request):
    items, categories, filters = filtered_transactions(request)
    account = get_active_account(request)
    incoming, outgoing = totals(items)
    return render(request, "cashbook/transactions.html", page_context(request,
        transactions=items, categories=categories, active_account=account, **filters,
        total_in=money(request.user, incoming, account=account), total_out=money(request.user, outgoing, account=account),
    ))

def transaction_excel_file(items, user, account):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Transactions"
    sheet.append(["Account", account.name, "Currency", account.currency])
    sheet.append([])
    sheet.append(["Date", "Type", "Category", "Description", f"Amount ({account.currency})"])
    for item in items:
        sheet.append([
            item.date,
            item.get_kind_display(),
            item.category,
            item.description,
            item.amount,
        ])
        for cell in sheet[sheet.max_row][1:4]:
            if isinstance(cell.value, str):
                cell.data_type = "s"

    header_fill = PatternFill("solid", fgColor="1D765D")
    for cell in sheet[3]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center")
    sheet.freeze_panes = "A4"
    sheet.auto_filter.ref = f"A3:E{sheet.max_row}"
    for column, width in {"A": 16, "B": 16, "C": 22, "D": 36, "E": 20}.items():
        sheet.column_dimensions[column].width = width
    for cell in sheet["A"][3:]:
        cell.number_format = {"dmy": "dd/mm/yyyy", "mdy": "mm/dd/yyyy", "ymd": "yyyy-mm-dd"}.get(
            user.date_format, "dd/mm/yyyy"
        )
    for cell in sheet["E"][3:]:
        cell.number_format = "#,##0.00"

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()

def transaction_pdf_file(items, user, account):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from xml.sax.saxutils import escape

    def pdf_text(value):
        text = str(value or "")
        # Standard PDF fonts do not contain every Indian script glyph. Keep
        # unsupported characters legible as Unicode escapes instead of failing.
        encoded = []
        for character in text:
            try:
                character.encode("cp1252")
            except UnicodeEncodeError:
                encoded.append(f"\\u{ord(character):04X}")
            else:
                encoded.append(character)
        return escape("".join(encoded)).replace("\n", "<br/>")

    output = BytesIO()
    document = SimpleDocTemplate(
        output, pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title="Cashbook Transactions",
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "TransactionCell", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8, leading=10, spaceAfter=0, alignment=TA_LEFT,
    )
    amount_style = ParagraphStyle(
        "TransactionAmount", parent=body_style, alignment=TA_RIGHT,
    )
    table_data = [[
        Paragraph("Date", body_style),
        Paragraph("Type", body_style),
        Paragraph("Category", body_style),
        Paragraph("Description", body_style),
        Paragraph(f"Amount ({escape(account.currency)})", amount_style),
    ]]
    date_format = PYTHON_DATE_FORMATS.get(user.date_format, "%d/%m/%Y")
    for item in items:
        table_data.append([
            Paragraph(pdf_text(item.date.strftime(date_format)), body_style),
            Paragraph(pdf_text(item.get_kind_display()), body_style),
            Paragraph(pdf_text(item.category), body_style),
            Paragraph(pdf_text(item.description), body_style),
            Paragraph(pdf_text(f"{item.amount:,.2f}"), amount_style),
        ])

    table = Table(table_data, colWidths=[25 * mm, 27 * mm, 38 * mm, 125 * mm, 34 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d765d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7f4")]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#1d765d")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#e3eae5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    document.build([
        Paragraph(pdf_text(f"Cashbook Transactions — {account.name} ({account.currency})"), styles["Title"]),
        Spacer(1, 6 * mm),
        table,
    ])
    return output.getvalue()

@login_required
def transactions_download(request):
    items, _, _ = filtered_transactions(request)
    account = get_active_account(request)
    export_format = request.GET.get("format", "")
    if export_format == "xlsx":
        response = HttpResponse(
            transaction_excel_file(items, request.user, account),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="cashbook-transactions.xlsx"'
        return response
    if export_format == "pdf":
        response = HttpResponse(transaction_pdf_file(items, request.user, account), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="cashbook-transactions.pdf"'
        return response
    return HttpResponseBadRequest("Choose an Excel or PDF download format.")

@login_required
def transaction_create(request):
    account = get_active_account(request)
    form = TransactionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.account = account
        item.save()
        messages.success(request, _("Transaction added to your cashbook."))
        return redirect("transactions")
    return render(request, "cashbook/form_page.html", page_context(
        request, form=form, title="Add transaction", eyebrow="Your money",
        submit_label="Save transaction", cancel_url=reverse("transactions"),
        transaction_account=account,
    ))

@login_required
def transaction_edit(request, pk):
    item = get_object_or_404(Transaction, pk=pk, user=request.user, account=get_active_account(request))
    form = TransactionForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Transaction updated."))
        return redirect("transactions")
    return render(request, "cashbook/form_page.html", page_context(
        request, form=form, title="Edit transaction", eyebrow="Your money",
        submit_label="Save changes", cancel_url=reverse("transactions"),
        transaction_account=item.account,
    ))

@login_required
def transaction_delete(request, pk):
    item = get_object_or_404(Transaction, pk=pk, user=request.user, account=get_active_account(request))
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
def basic_calculator(request):
    return render(request, "cashbook/basic_calculator.html", page_context(request))

@login_required
def cash_calculator(request):
    account = get_active_account(request)
    denominations = CASH_DENOMINATIONS.get(account.currency, CASH_DENOMINATIONS["INR"])
    return render(request, "cashbook/calculator.html", page_context(
        request,
        denominations=[{"value": value} for value in denominations],
        active_account=account,
    ))

@login_required
def currency_converter(request):
    account = get_active_account(request)
    currencies = [
        {"code": code, "name": str(label)}
        for code, label in request.user.CURRENCY_CHOICES
    ]
    target_currency = "USD" if account.currency != "USD" else "INR"
    return render(request, "cashbook/currency_converter.html", page_context(
        request,
        currencies=currencies,
        target_currency=target_currency,
        active_account=account,
    ))

@login_required
def settings(request):
    action = request.POST.get("action", "") if request.method == "POST" else ""
    selected_tab = request.GET.get("tab", "")
    tab_names = {"dark_mode": "dark-mode", "language": "language", "date_format": "date-format", "time_format": "time-format", "currency_format": "currency-format"}
    valid_tabs = {"profile", "dark-mode", "language", "date-format", "time-format", "currency-format", "about", "privacy-policy"}
    tab = tab_names.get(action, selected_tab if selected_tab in valid_tabs else "profile")
    form = ProfileForm(request.POST if request.method == "POST" and action == "profile" else None, instance=request.user)
    language_form = LanguageForm(request.POST if action == "language" else None, instance=request.user)
    date_format_form = DateFormatForm(request.POST if action == "date_format" else None, instance=request.user)
    dark_mode_form = DarkModeForm(request.POST if action == "dark_mode" else None, instance=request.user)
    time_format_form = TimeFormatForm(request.POST if action == "time_format" else None, instance=request.user)
    currency_format_form = CurrencyFormatForm(request.POST if action == "currency_format" else None, instance=request.user)
    if request.method == "POST" and action == "language" and language_form.is_valid():
        language_form.save()
        messages.success(request, _("Your language preference has been saved."))
        return redirect("/settings/?tab=language")
    if request.method == "POST" and action == "date_format" and date_format_form.is_valid():
        date_format_form.save()
        messages.success(request, _("Your date format preference has been saved."))
        return redirect("/settings/?tab=date-format")
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
        request, form=form, language_form=language_form, date_format_form=date_format_form, dark_mode_form=dark_mode_form,
        time_format_form=time_format_form, currency_format_form=currency_format_form, tab=tab,
    ))
