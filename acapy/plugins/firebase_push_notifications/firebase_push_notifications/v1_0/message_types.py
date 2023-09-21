from aries_cloudagent.protocols.didcomm_prefix import DIDCommPrefix

ARIES_PROTOCOL = "push-notifications-fcm/1.0"
SET_DEVICE_INFO = f"{ARIES_PROTOCOL}/set-device-info"
PROTOCOL_PACKAGE = "firebase_push_notifications.v1_0"

MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
        SET_DEVICE_INFO: f"{PROTOCOL_PACKAGE}.messages.set_device_info.SetDeviceInfo",
    },
)
