import logging

from aries_cloudagent.messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
)

from ..messages.set_device_info import SetDeviceInfo
from ..manager import save_device_token

LOGGER = logging.getLogger(__name__)


class SetDeviceInfoHandler(BaseHandler):
    """Message handler class for push notifications."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        connection_id = context.connection_record.connection_id
        LOGGER.info(
            f'set-device-info protocol handler called for connection: {connection_id}')
        assert isinstance(context.message, SetDeviceInfo)

        device_token = context.message.device_token
        device_platform = context.message.device_platform

        await save_device_token(context.profile, device_token, connection_id)

        await responder.send_reply(SetDeviceInfo(device_token=device_token, device_platform=device_platform))
