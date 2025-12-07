from data_models.events_models import EventDataModel
from django.db import models

from apps.accounts.models import User


class EventStatus(models.TextChoices):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventRegistrationStatus(models.TextChoices):
    REGISTERED = "registered"
    CANCELLED = "cancelled"
    PENDING = "pending"
    REJECTED = "rejected"
    CHECKED_IN = "checked_in"
    NOT_ATTENDED = "not_attended"


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date = models.DateTimeField()
    location = models.CharField(max_length=255, verbose_name="Address")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.SCHEDULED,
    )
    duration = models.DurationField(null=True, blank=True)
    max_capacity = models.PositiveIntegerField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "account_category"

    def __str__(self):
        return self.title

    def to_pydantic(self) -> EventDataModel:
        duration_minutes = (
            int(self.duration.total_seconds() // 60) if self.duration else None
        )
        date_str = self.date.strftime("%d %b %Y, %H:%M")

        return EventDataModel(
            id=self.id,
            title=self.title,
            description=self.description,
            date=date_str,
            location=self.location,
            status=self.status,
            duration=duration_minutes,
            max_capacity=self.max_capacity,
            is_draft=self.is_draft,
            organizer=str(self.organizer),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    status = models.CharField(
        max_length=20,
        choices=EventRegistrationStatus.choices,
        default=EventRegistrationStatus.REGISTERED,
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("event", "user")

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
