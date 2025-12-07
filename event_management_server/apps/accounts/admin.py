from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated

from apps.accounts.models import User
from apps.events.models import EventRegistration


class EventRegistrationUserInline(TabularInlinePaginated):
    model = EventRegistration
    per_page = 5
    readonly_fields = ("event", "status", "registered_at", "cancelled_at")
    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "is_active")
    list_display_links = ("id", "first_name", "last_name")
    readonly_fields = ("password",)
    inlines = [
        EventRegistrationUserInline,
    ]
    fieldsets = (
        (
            "Main information",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    (
                        "first_name",
                        "last_name",
                    ),
                    "phone_number",
                ),
            },
        ),
        (
            "Statuses",
            {
                "classes": ("wide",),
                "fields": ("is_active",),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = self.model.objects.get_queryset()
        queryset = queryset.filter(is_staff=False)
        return queryset


admin.site.register(User, AccountAdmin)
