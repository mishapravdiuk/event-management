from api.api_core.endpoints.accounts_api import accounts_router
from api.api_core.endpoints.events_api import events_router
from api.api_core.routes import EnumBaseRoutes
from ninja import Router

api_v1_router = Router()

api_v1_router.add_router(
    EnumBaseRoutes.ACCOUNTS, router=accounts_router, tags=["accounts"]
)
api_v1_router.add_router(EnumBaseRoutes.EVENTS, router=events_router, tags=["events"])
