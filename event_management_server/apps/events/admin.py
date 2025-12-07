from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated

from apps.events.models import Event, EventRegistration


class EventRegistrationInline(TabularInlinePaginated):
    model = EventRegistration
    per_page = 5
    readonly_fields = ("event", "status", "registered_at", "cancelled_at")
    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "date",
        "status",
        "organizer",
    )
    list_display_links = ("id", "title")
    fields = (
        "title",
        "description",
        "date",
        "location",
        "organizer",
        "status",
        "duration",
        "max_capacity",
        "is_draft",
    )
    list_filter = (
        "status",
        "date",
    )
    search_fields = (
        "title",
        "location",
        "description",
        "organizer__username",
        "organizer__email",
    )
    ordering = ("-date",)
    inlines = [EventRegistrationInline]


class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "user",
        "status",
    )
    list_display_links = ("id",)
    fileds = (
        "event",
        "user",
        "status",
        "registered_at",
        "cancelled_at",
    )
    list_filter = ("status",)
    search_fields = ("event__title", "user__username", "user__email")
    readonly_fields = ("registered_at", "cancelled_at")
    ordering = ("-registered_at",)


admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
