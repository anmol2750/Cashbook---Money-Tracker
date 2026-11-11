from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import CalendarEvent, Note, Transaction, TransactionAccount, User

class CashbookAdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

@admin.register(User)
class CashbookUserAdmin(UserAdmin):
    add_form = CashbookAdminCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_active", "currency", "currency_format", "time_format", "dark_mode", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser", "dark_mode")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal info", {"fields": ("first_name", "last_name", "currency", "currency_format", "time_format", "language", "dark_mode")}), ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("Important dates", {"fields": ("last_login", "date_joined")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
    search_fields = ("email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "account", "kind", "category", "amount")
    list_filter = ("kind", "account", "date")
    search_fields = ("user__email", "account__name", "category", "description")
    date_hierarchy = "date"

@admin.register(TransactionAccount)
class TransactionAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "currency", "is_default", "created_at")
    list_filter = ("currency", "is_default")
    search_fields = ("name", "user__email")

admin.site.register(Note)
admin.site.register(CalendarEvent)
