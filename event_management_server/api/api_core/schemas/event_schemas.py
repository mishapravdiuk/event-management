from enum import Enum
from typing import Optional

from ninja import Schema
from pydantic import Field


class EventStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventSchema(Schema):
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    date: str = Field(..., description="Event datetime in ISO format")
    location: str = Field(..., description="Event address")
    status: EventStatusEnum = Field(..., description="Event status")
    duration: Optional[int] = Field(
        None,
        description="Event duration in minutes",
    )
    max_capacity: Optional[int] = Field(
        None,
        description="Maximum number of participants",
    )
    is_draft: bool = Field(..., description="Draft status")


class EventFiltersSchema(Schema):
    statuses: Optional[str] = None
    organizer_id: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    q: Optional[str] = None
