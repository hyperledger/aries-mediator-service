from datetime import timedelta
from dateutil import parser
import logging
import json
import os
import requests

import google.auth.transport.requests
from google.oauth2 import service_account

from aries_cloudagent.messaging.util import time_now, datetime_now
from .models import FirebaseConnectionRecord

from .constants import SCOPES, BASE_URL, ENDPOINT_PREFIX, ENDPOINT_SUFFIX, MAX_SEND_RATE_MINUTES

PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
FCM_ENDPOINT = ENDPOINT_PREFIX + PROJECT_ID + ENDPOINT_SUFFIX
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT

LOGGER = logging.getLogger(__name__)

""" Gets an access token for sending firebase messages with the service account credentials """
def _get_access_token():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT')), scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

""" Attempt to send a push notification to the device associated with the connection id if passes the following checks"""
async def send_message(profile, connection_id):
    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8'
    }

    try:
        async with profile.session() as session:
            record = await FirebaseConnectionRecord.retrieve_by_connection_id(session, connection_id)

            """ Don't send token if it is blank. This is the same as being disabled """
            if record.device_token == '':
                return

            """ 
                To avoid spamming the user with push notifications, 
                we will only send a push notification if the last one was sent more than MAX_SEND_RATE_MINUTES minutes ago. 
            """
            if record.sent_time is not None and parser.parse(record.sent_time) > datetime_now() - timedelta(minutes=MAX_SEND_RATE_MINUTES):
                LOGGER.info(
                    f'Connection {connection_id} was sent a push notification within the last {MAX_SEND_RATE_MINUTES} minutes. Skipping.')
                return
            
            LOGGER.info(
                f'Sending push notification to firebase from connection: {connection_id}')

            resp = requests.post(FCM_URL, data=json.dumps({
                "message": {
                    "token": record.device_token,
                    "notification": {
                        "title": os.environ.get('FIREBASE_NOTIFICATION_TITLE'),
                        "body": os.environ.get('FIREBASE_NOTIFICATION_BODY')
                    },
                    "apns": {
                        "payload": {
                            "aps": {
                                "alert": {
                                    "title": os.environ.get('FIREBASE_NOTIFICATION_TITLE'),
                                    "body": os.environ.get('FIREBASE_NOTIFICATION_BODY')
                                },
                                "badge": 1
                            }
                        }
                    }
                }
            }), headers=headers)

            if resp.status_code == 200:
                LOGGER.info(
                    f'Successfully sent message to firebase for delivery. response: {resp.text}')
                record.sent_time = time_now()
                await record.save(session, reason="Sent push notification")
            else:
                LOGGER.error(
                    f'Unable to send message to Firebase. response: {resp.text}')
    except Exception as e:
        LOGGER.error(
            f'Error retrieving device token for connection: {connection_id}')
        LOGGER.error(e)
        return

""" Save or update the device token for the connection id """
async def save_device_token(profile, token, connection_id):
    conn_token_obj = {
        'connection_id': connection_id,
        'device_token': token,
    }

    LOGGER.info(f'Saving device token for connection: {connection_id}')

    conn_token_record: FirebaseConnectionRecord = FirebaseConnectionRecord.deserialize(
        conn_token_obj)

    try:
        async with profile.session() as session:
            records = await FirebaseConnectionRecord.query(
                session,
                {
                    "connection_id": connection_id
                },
            )

            if (len(records) == 0):
                await conn_token_record.save(session, reason="Saving device token")
            elif records[0].device_token != token:
                records[0].device_token = token
                await records[0].save(session, reason="Updating device token")
    except Exception as e:
        LOGGER.error(
            f'Error saving device token for connection: {connection_id}')
        LOGGER.error(e)
