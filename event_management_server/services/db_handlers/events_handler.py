from apps.events.models import Event, EventRegistration, EventRegistrationStatus
from django.db.models import Q
from datetime import datetime, timedelta
from api.api_core.utils.exceptions import EventDoesNotExistError, CannotUpdateOtherEvent, RegistrationNotFoundError
from api.api_core.schemas.event_schemas import EventSchema
from apps.accounts.models import User

class EventsHandler:
    @staticmethod
    def get_event_obj(event_id: int) -> Event:
        try:
            event = Event.objects.get(id=event_id)
        except:
            raise EventDoesNotExistError()
        return event
    
    @staticmethod
    def create_event(user, payload: EventSchema):
        event = Event.objects.create(
            title=payload.title,
            description=payload.description,
            date=datetime.fromisoformat(payload.date),
            location=payload.location,
            status=payload.status.value,
            duration=timedelta(minutes=payload.duration) if payload.duration else None,
            max_capacity=payload.max_capacity,
            is_draft=payload.is_draft,
            organizer=user,
        )
        
        return event

    @staticmethod
    def update_event(event_id: int, user: User, payload: EventSchema) -> Event:
        event = EventsHandler.get_event_obj(event_id)
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


    @staticmethod
    def get_events_list(request, filters_query) -> list[Event]:
        filters = Q()
        
        if filters_query.statuses:
            status_list = [s.strip() for s in filters_query.statuses.split(",") if s.strip()]
            if status_list:
                filters &= Q(status__in=status_list)

        if filters_query.organizer_id:
            filters &= Q(organizer_id=filters_query.organizer_id)

        if filters_query.date_from:
            try:
                date_from = datetime.fromisoformat(filters_query.date_from)
                filters &= Q(date__gte=date_from)
            except Exception:
                # ignore bad date or optionally raise 400
                pass

        if filters_query.date_to:
            try:
                date_to = datetime.fromisoformat(filters_query.date_to)
                filters &= Q(date__lte=date_to)
            except Exception:
                pass
        
        qs = Event.objects.filter(filters).order_by("id")
        events_list = []
        
        for event in qs:
            pd = event.to_pydantic()
            if hasattr(pd, "dict"):
                event_dict = pd.dict()
            else:
                event_dict = dict(pd)
            
            if isinstance(event_dict.get("date"), (datetime,)):
                event_dict["date"] = event_dict["date"].isoformat()
            if event_dict.get("created_at") and isinstance(event_dict["created_at"], datetime):
                event_dict["created_at"] = event_dict["created_at"].isoformat()
            if event_dict.get("updated_at") and isinstance(event_dict["updated_at"], datetime):
                event_dict["updated_at"] = event_dict["updated_at"].isoformat()

            event_schema = EventSchema(**event_dict)
            events_list.append(event_schema)

        return events_list
    
    @staticmethod
    def register_user(user, event_id: int) -> Event:
        event = EventsHandler.get_event_obj(event_id)
        EventRegistration.objects.create(user=user, event=event)
        return event.to_pydantic()
    
    @staticmethod
    def cancel_registration(user, event_id: int) -> Event:
        event = EventsHandler.get_event_obj(event_id)
        events = EventRegistration.objects.filter(user=user, event=event)
        if events.exists():
            event_registration_obj = events.first()
            event_registration_obj.status = EventRegistrationStatus.CANCELLED
            event_registration_obj.cancelled_at = datetime.now()
            event_registration_obj.save()
        else:
            raise RegistrationNotFoundError()
        
        return event.to_pydantic()