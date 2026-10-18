from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import CalendarEvent, Note, Transaction, User

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

class TransactionForm(StyledFormMixin, forms.ModelForm):
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
            "category": forms.TextInput(attrs={"placeholder": _("e.g. Salary, Food, Travel")}),
            "description": forms.TextInput(attrs={"placeholder": _("Add a short note (optional)")}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["kind"].label = _("Transaction type")

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

class CurrencyFormatForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("currency_format",)
        labels = {"currency_format": _("Currency display")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
