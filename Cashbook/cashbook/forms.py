from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import CalendarEvent, Note, Transaction, TransactionAccount, User

class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " input").strip()

class EmailLoginForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

class SignUpForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {"email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["first_name"].required = True
        self.fields["first_name"].widget.attrs["placeholder"] = _("First name")
        self.fields["last_name"].widget.attrs["placeholder"] = _("Last name")
        self.fields["password1"].widget.attrs.update({"autocomplete": "new-password", "placeholder": _("At least 8 characters")})
        self.fields["password2"].widget.attrs.update({"autocomplete": "new-password", "placeholder": _("Repeat your password")})
    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

class VerificationResendForm(StyledFormMixin, forms.Form):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

class VerificationOTPForm(StyledFormMixin, forms.Form):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}),
    )
    code = forms.RegexField(
        regex=r"^[0-9]{6}$",
        label=_("Six-digit verification code"),
        error_messages={"invalid": _("Enter the 6-digit code from your email.")},
        widget=forms.TextInput(attrs={
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "pattern": "[0-9]{6}",
            "maxlength": "6",
            "placeholder": "000000",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

class TransactionForm(StyledFormMixin, forms.ModelForm):
    OTHER_CATEGORY = "__other__"
    PRESET_CATEGORIES = (
        "Bills", "Utilities", "Rent", "Health", "Fitness", "Education",
        "Travel", "Gifts", "Insurance",
    )
    category = forms.ChoiceField(
        choices=[("", _("Select a category"))]
        + [(category, _(category)) for category in PRESET_CATEGORIES]
        + [(OTHER_CATEGORY, _("Others"))],
        widget=forms.Select(attrs={"data-category-select": "true"}),
    )
    other_category = forms.CharField(
        max_length=60,
        required=False,
        label=_("Enter your category"),
        widget=forms.TextInput(attrs={"placeholder": _("e.g. Pet care")}),
    )
    amount = forms.DecimalField(
        min_value=Decimal("0.01"),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"min": "0.01", "step": "0.01", "placeholder": "0.00"}),
    )
    class Meta:
        model = Transaction
        fields = ("kind", "amount", "category", "description", "date")
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": _("Add a short note (optional)")}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["kind"].label = _("Transaction type")
        self.order_fields(("kind", "amount", "category", "other_category", "description", "date"))
        if self.instance.pk:
            category = self.instance.category
            if category in self.PRESET_CATEGORIES:
                self.initial["category"] = category
            else:
                self.initial["category"] = self.OTHER_CATEGORY
                self.initial["other_category"] = category
        else:
            self.initial["category"] = ""

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("category") == self.OTHER_CATEGORY:
            custom_category = (cleaned_data.get("other_category") or "").strip()
            if not custom_category:
                self.add_error("other_category", _("Enter a category."))
            else:
                cleaned_data["category"] = custom_category
        return cleaned_data

class NoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": _("Give your note a title")}),
            "content": forms.Textarea(attrs={"placeholder": _("Write down an idea, reminder, or anything to remember…"), "rows": 7}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class CalendarEventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ("title", "date", "time", "details")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": _("e.g. Rent due")}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "details": forms.TextInput(attrs={"placeholder": _("Add a detail (optional)")}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["time"].required = False

class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "currency")
        labels = {"currency": _("Default currency for new accounts")}
        widgets = {"first_name": forms.TextInput(attrs={"placeholder": _("First name")}), "last_name": forms.TextInput(attrs={"placeholder": _("Last name")})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class LanguageForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("language",)
        labels = {"language": _("Display language")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class DarkModeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("dark_mode",)
        labels = {"dark_mode": _("Enable dark mode")}
        widgets = {"dark_mode": forms.CheckboxInput(attrs={"class": "theme-switch-input"})}

class TimeFormatForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("time_format",)
        labels = {"time_format": _("Time display")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class DateFormatForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("date_format",)
        labels = {"date_format": _("Date display")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class CurrencyFormatForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("currency_format",)
        labels = {"currency_format": _("Currency display")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

class TransactionAccountForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TransactionAccount
        fields = ("name", "currency")
        labels = {"name": _("Account name"), "currency": _("Currency")}
        widgets = {"name": forms.TextInput(attrs={"placeholder": _("e.g. Cash wallet or Savings account")})}

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["currency"].initial = user.currency

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError(_("Enter an account name."))
        existing = TransactionAccount.objects.filter(user=self.user, name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError(_("You already have an account with this name."))
        return name

class TransactionAccountNameForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TransactionAccount
        fields = ("name",)
        labels = {"name": _("Account name")}
        widgets = {"name": forms.TextInput(attrs={"placeholder": _("e.g. Savings account")})}

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError(_("Enter an account name."))
        existing = TransactionAccount.objects.filter(user=self.user, name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError(_("You already have an account with this name."))
        return name
