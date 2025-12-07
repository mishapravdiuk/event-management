from datetime import datetime, timedelta
from typing import List

from api.api_core.routes import EnumDetailRoutes
from api.api_core.schemas.error_schemas import BadResponse
from api.api_core.schemas.event_schemas import EventFiltersSchema, EventSchema
from api.api_core.schemas.response_schema import SuccessResponse
from api.api_core.utils.exceptions import (
    CannotDeleteOtherEvent,
    CannotUpdateOtherEvent,
    EventDoesNotExistError,
)
from apps.events.models import Event
from ninja import Query, Router
from services.db_handlers.accounts_handler import AccountsHandler
from services.db_handlers.events_handler import EventsHandler

events_router = Router()


@events_router.get(
    path=EnumDetailRoutes.GET_EVENT_INFO_BY_ID,
    summary="Get event information",
    response={
        200: EventSchema,
        (400, 404): BadResponse,
    },
)
def get_event_info(request, event_id: int):
    event = EventsHandler.get_event_obj(event_id)
    return event.to_pydantic()


@events_router.post(
    path=EnumDetailRoutes.CREATE_EVENT,
    summary="Create a new event",
    response={
        (200, 201): EventSchema,
        (400, 404): BadResponse,
    },
)
def create_event(request, payload: EventSchema):
    user = AccountsHandler.get_user_by_id(request)
    event = EventsHandler.create_event(user, payload)

    return event.to_pydantic()


@events_router.put(
    path=EnumDetailRoutes.UPDATE_EVENT,
    summary="Update event",
    response={
        200: EventSchema,
        (400, 404): BadResponse,
    },
)
def update_event(request, event_id: int, payload: EventSchema):
    user = AccountsHandler.get_user_by_id(request)
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise EventDoesNotExistError()

    if event.organizer != user:
        raise CannotUpdateOtherEvent()

    event.title = payload.title
    event.description = payload.description
    event.date = datetime.fromisoformat(payload.date)
    event.location = payload.location
    event.status = payload.status.value
    event.duration = timedelta(minutes=payload.duration) if payload.duration else None
    event.max_capacity = payload.max_capacity
    event.is_draft = payload.is_draft

    event.save()

    return event.to_pydantic()


@events_router.delete(
    path=EnumDetailRoutes.DELETE_EVENT,
    summary="Delete event",
    response={
        (200): SuccessResponse,
        (400, 404): BadResponse,
    },
)
def delete_event(request, event_id: int):
    user = AccountsHandler.get_user_by_id(request)
    event = EventsHandler.get_event_obj(event_id)
    if event.organizer != user:
        raise CannotDeleteOtherEvent()

    event.delete()
    return SuccessResponse()


@events_router.get(
    EnumDetailRoutes.GET_EVENTS_LIST,
    summary="Get list of events",
    response={200: List[EventSchema], (400, 404, 422): BadResponse},
)
def get_events_list_route(request, filters: EventFiltersSchema = Query(...)):
    return EventsHandler.get_events_list(request=request, filters_query=filters)


@events_router.get(
    EnumDetailRoutes.USER_REGISTRATION,
    summary="Register user for an event",
    response={200: EventSchema, (400, 404, 422): BadResponse},
)
def get_register_user(request, event_id: int):
    user = AccountsHandler.get_user_by_id(request)
    return EventsHandler.register_user(user, event_id)


@events_router.get(
    EnumDetailRoutes.CANCEL_USER_REGISTRATION,
    summary="Cancel user registration for an event",
    response={200: EventSchema, (400, 404, 422): BadResponse},
)
def get_cancel_user_registration(request, event_id: int):
    user = AccountsHandler.get_user_by_id(request)
    return EventsHandler.cancel_registration(user, event_id)
