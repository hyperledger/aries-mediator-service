import logging
import re

from aiohttp import web
from aiohttp_apispec import docs, match_info_schema, request_schema, response_schema
from marshmallow import fields

from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.storage.error import StorageNotFoundError
from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.profile import Profile

from .manager import save_device_token, send_message
from .constants import FORWARDING_EVENT

LOGGER = logging.getLogger(__name__)


"""
    Event bus registration and handling
"""


def register_events(event_bus: EventBus):
    LOGGER.info("Registering firebase service on forwarding event")
    event_bus.subscribe(re.compile(FORWARDING_EVENT), handle_event_forwarding)


async def handle_event_forwarding(profile: Profile, event: Event):
    print(
        f'handling event forwarding of connection {event.payload["connection_id"]}')
    await send_message(profile, event.payload["connection_id"])


"""
    Shared schemas
"""


class BasicConnIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking connection id."""

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )


"""
    Send push notification
"""


class SendRequestSchema(OpenAPISchema):
    """Schema to allow serialization/deserialization of push notifcation send request."""


class SendResponseSchema(OpenAPISchema):
    """Schema to allow serialization/deserialization of push notifcation send request."""


@docs(tags=["push-notification"], summary="Send a push notification to the device of the connection")
@request_schema(SendRequestSchema())
@response_schema(SendResponseSchema(), 200, description="")
async def send_push_notification(request: web.BaseRequest):
    connection_id = request.match_info["conn_id"]
    LOGGER.info(
        f"Sending push notification to connection {connection_id} from api")
    send_message(connection_id)
    return web.json_response()


"""
    Set push notification device info
"""


class SetDeviceRequestSchema(OpenAPISchema):
    """Schema to allow serialization/deserialization of device info request."""
    device_token = fields.Str(
        required=True,
        description="Mobile firebase push token",
        example="kMCFR-6R6GTfH_XeuXy5v:APA91bHqZgXLV3VtxOxXGy1Sq14_jU5Yhnhc6kTDlF2At3IcuxNK1_kmjak9_f2WAJ8bJHV2GSJj6DBT60j_BqrdTOi9sXIcWEtSBNiJ1vyr9BG0IEsmDuqO4jkIDGNbe2kU_LZf8Q24"
    )


class SetDeviceResponseSchema(OpenAPISchema):
    """Schema to allow serialization/deserialization of device info request."""


@docs(tags=["push-notification"], summary="Set device info of the connection")
@match_info_schema(BasicConnIdMatchInfoSchema())
@request_schema(SetDeviceRequestSchema())
@response_schema(SetDeviceResponseSchema(), 200, description="")
async def set_connection_device_info(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]

    try:
        async with context.profile.session() as session:
            await ConnRecord.retrieve_by_id(session, connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    try:
        await save_device_token(context.profile, request.get('device_token'), connection_id)
    except Exception as e:
        raise web.HTTPBadRequest(reason=e)

    return web.json_response({'success': True})


"""
    Routes
"""


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [web.post("/push-notification-fcm/1.0/{conn_id}/send",
                  send_push_notification)]
    )
    app.add_routes(
        [web.post("/push-notification-fcm/1.0/{conn_id}/set_device_info",
                  set_connection_device_info)]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "fcm-push-notification",
            "description": "Firebase push notification v1.0",
        }
    )
