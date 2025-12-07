from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventDataModel(BaseModel):
    id: int = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    date: str = Field(..., description="Event datetime")
    location: str = Field(..., description="Event address")
    status: str = Field(..., description="Event status")
    duration: Optional[int] = Field(
        None,
        description="Event duration in minutes",
    )
    max_capacity: Optional[int] = Field(
        None,
        description="Maximum number of participants",
    )
    is_draft: bool = Field(..., description="Draft status")
    organizer: str = Field(..., description="Event organizer")
    created_at: datetime = Field(..., description="Created at time")
    updated_at: datetime = Field(..., description="Updated at time")
