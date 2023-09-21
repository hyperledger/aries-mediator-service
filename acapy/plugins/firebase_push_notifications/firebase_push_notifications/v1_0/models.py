from marshmallow import fields

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import INDY_ISO8601_DATETIME


class FirebaseConnectionRecord(BaseRecord):
    """Firebase Connection Record."""

    RECORD_ID_NAME = "record_id"
    RECORD_TYPE = "push_notification_record"
    TAG_NAMES = {"connection_id", "device_token", "sent_time"}

    class Meta:
        """FirebaseConnectionRecord metadata."""

        schema_class = "FirebaseConnectionRecordSchema"

    def __init__(
        self,
        *,
        record_id: str = None,
        connection_id: str = None,
        device_token: str = None,
        sent_time: str = None,
        **kwargs
    ):
        """Initialize a new SchemaRecord."""
        super().__init__(record_id, None, **kwargs)
        self.connection_id = connection_id
        self.device_token = device_token
        self.sent_time = sent_time

    @property
    def record_id(self) -> str:
        """Accessor for this schema's id."""
        return self._id

    @classmethod
    async def retrieve_by_connection_id(
        cls, session: ProfileSession, connection_id: str
    ) -> "FirebaseConnectionRecord":
        """Retrieve a firebase connection record by connection ID."""
        tag_filter = {"connection_id": connection_id}
        return await cls.retrieve_by_tag_filter(session, tag_filter)


class FirebaseConnectionRecordSchema(BaseRecordSchema):
    class Meta:
        model_class = FirebaseConnectionRecord

    connection_id = fields.Str(required=True)
    device_token = fields.Str(required=True)
    sent_time = fields.Str(required=False, **INDY_ISO8601_DATETIME)
