from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import CalendarEvent, Note, Transaction, User

class CashbookAdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

@admin.register(User)
class CashbookUserAdmin(UserAdmin):
    add_form = CashbookAdminCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "currency", "currency_format", "time_format", "dark_mode", "is_staff")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal info", {"fields": ("first_name", "last_name", "currency", "currency_format", "time_format", "language", "dark_mode")}), ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("Important dates", {"fields": ("last_login", "date_joined")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
    search_fields = ("email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions")

admin.site.register(Transaction)
admin.site.register(Note)
admin.site.register(CalendarEvent)
