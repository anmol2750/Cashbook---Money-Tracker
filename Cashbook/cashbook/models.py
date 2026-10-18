from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have staff and superuser access.")
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    LANGUAGE_CHOICES = [("en", _("English")), ("hi", _("Hindi (हिन्दी)"))]
    CURRENCY_CHOICES = [
        ("INR", _("Indian Rupee (₹)")), ("USD", _("US Dollar ($)")), ("EUR", _("Euro (€)")),
        ("GBP", _("British Pound (£)")), ("CAD", _("Canadian Dollar (C$)")), ("AUD", _("Australian Dollar (A$)")),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="INR")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    dark_mode = models.BooleanField(default=False)
    TIME_FORMAT_CHOICES = [("12h", _("12-hour")), ("24h", _("24-hour"))]
    CURRENCY_FORMAT_CHOICES = [("symbol", _("Currency symbol")), ("code", _("Currency code"))]
    time_format = models.CharField(max_length=3, choices=TIME_FORMAT_CHOICES, default="12h")
    currency_format = models.CharField(max_length=6, choices=CURRENCY_FORMAT_CHOICES, default="symbol")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email).lower()
        super().save(*args, **kwargs)
    @property
    def display_name(self):
        return self.get_full_name().strip() or self.email.split("@")[0]
    def __str__(self):
        return self.email

class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    TYPE_CHOICES = [(INCOME, _("Cash in")), (EXPENSE, _("Cash out"))]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    kind = models.CharField(max_length=8, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    category = models.CharField(max_length=60, default="General")
    description = models.CharField(max_length=180, blank=True)
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"{self.get_kind_display()} · {self.amount}"

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-updated_at"]
    def __str__(self):
        return self.title

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calendar_events")
    title = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    details = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["date", "time", "title"]
    def __str__(self):
        return self.title
