from enum import Enum

API_BASE = "api/"
API_PREFIX = "event-management-server/"


class EnumBaseRoutes(str, Enum):
    ACCOUNTS = "/accounts"
    EVENTS = "/events"


class EnumDetailRoutes(str, Enum):
    REGISTER_USER = "/register"
    AUTH_LOGIN = "/login"

    # events
    GET_EVENT_INFO_BY_ID = "/get_event_info_by_id"
    CREATE_EVENT = "/create_event"
    UPDATE_EVENT = "/update_event"
    DELETE_EVENT = "/delete_event"
    GET_EVENTS_LIST = "/get_all_events"

    USER_REGISTRATION = "/user_registration"
    CANCEL_USER_REGISTRATION = "/cancel_user_registration"
