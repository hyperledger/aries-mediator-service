from marshmallow import EXCLUDE, fields

from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import PROTOCOL_PACKAGE, SET_DEVICE_INFO

HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers.handler.SetDeviceInfoHandler"
)


class SetDeviceInfo(AgentMessage):
    """Class defining the structure of a set device info message."""

    class Meta:
        """Metadata for a set device info message."""
        handler_class = HANDLER_CLASS
        message_type = SET_DEVICE_INFO
        schema_class = "SetDeviceInfoSchema"

    def __init__(
        self,
        *,
        device_token: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.device_token = device_token


class SetDeviceInfoSchema(AgentMessageSchema):

    class Meta:
        model_class = SetDeviceInfo
        unknown = EXCLUDE

    device_token = fields.Str(
        required=True,
        description="Firebase device token",
        example="kMCFR-6R6GTfH_XeuXy5v:APA91bHqZgXLV3VtxOxXGy1Sq14_jU5Yhnhc6kTDlF2At3IcuxNK1_kmjak9_f2WAJ8bJHV2GSJj6DBT60j_BqrdTOi9sXIcWEtSBNiJ1vyr9BG0IEsmDuqO4jkIDGNbe2kU_LZf8Q24"
    )
