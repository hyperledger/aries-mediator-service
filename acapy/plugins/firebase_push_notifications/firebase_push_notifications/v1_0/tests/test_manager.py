import os
import asynctest
import mock
from datetime import timedelta

from aries_cloudagent.core.in_memory import InMemoryProfile
from aries_cloudagent.messaging.util import datetime_now, datetime_to_str

from ..models import FirebaseConnectionRecord
from ..constants import MAX_SEND_RATE_MINUTES
from ..manager import send_message


class TestManager(asynctest.TestCase):
    async def setUp(self):
        self.profile = InMemoryProfile.test_profile()
        self.context = self.profile.context
        self.test_conn_id = "connection-id"

    @asynctest.patch('requests.post')
    @asynctest.patch.object(FirebaseConnectionRecord, 'save')
    @asynctest.patch.object(FirebaseConnectionRecord, 'retrieve_by_connection_id')
    async def test_send_message_should_retrieve_send_push_and_save_for_valid_connection_with_no_last_sent_time(self, mock_retrieve, mock_save, mock_post):
        mock_retrieve.return_value = FirebaseConnectionRecord(
            connection_id=self.test_conn_id,
            sent_time=None,
            device_token="device-token"
        )
        mock_post.return_value = mock.Mock(status_code=200)
        await send_message(self.profile, self.test_conn_id)

        assert mock_retrieve.await_count == 1
        assert mock_post.called
        assert mock_save.await_count == 1

    @asynctest.patch('requests.post')
    @asynctest.patch.object(FirebaseConnectionRecord, 'save')
    @asynctest.patch.object(FirebaseConnectionRecord, 'retrieve_by_connection_id')
    async def test_send_message_should_do_nothing_when_retrieved_device_token_is_blank(self, mock_retrieve, mock_save, mock_post):
        mock_retrieve.return_value = FirebaseConnectionRecord(
            connection_id=self.test_conn_id,
            sent_time=None,
            device_token=""
        )
        mock_post.return_value = mock.Mock(status_code=200)
        await send_message(self.profile, self.test_conn_id)

        assert mock_retrieve.await_count == 1
        assert not mock_post.called
        assert mock_save.await_count == 0

    @asynctest.patch('requests.post')
    @asynctest.patch.object(FirebaseConnectionRecord, 'save')
    @asynctest.patch.object(FirebaseConnectionRecord, 'retrieve_by_connection_id')
    async def test_send_message_should_do_nothing_for_second_message_less_than_configured_time(self, mock_retrieve, mock_save, mock_post):
        mock_retrieve.return_value = FirebaseConnectionRecord(
            connection_id=self.test_conn_id,
            sent_time=datetime_to_str(
                datetime_now() - timedelta(minutes=MAX_SEND_RATE_MINUTES - 1)),
            device_token="device-token"
        )
        mock_post.return_value = mock.Mock(status_code=200)
        await send_message(self.profile, self.test_conn_id)

        assert mock_retrieve.await_count == 1
        assert not mock_post.called
        assert mock_save.await_count == 0

    @asynctest.patch('requests.post')
    @asynctest.patch.object(FirebaseConnectionRecord, 'save')
    @asynctest.patch.object(FirebaseConnectionRecord, 'retrieve_by_connection_id')
    async def test_send_message_should_retrieve_send_push_and_save_for_valid_connection_with_sent_time_greater_than_configured_time(self, mock_retrieve, mock_save, mock_post):
        mock_retrieve.return_value = FirebaseConnectionRecord(
            connection_id=self.test_conn_id,
            sent_time=datetime_to_str(
                datetime_now() - timedelta(minutes=MAX_SEND_RATE_MINUTES + 1)),
            device_token="device-token"
        )
        mock_post.return_value = mock.Mock(status_code=200)
        await send_message(self.profile, self.test_conn_id)

        assert mock_retrieve.await_count == 1
        assert mock_post.called
        assert mock_save.await_count == 1

    @asynctest.patch('requests.post')
    @asynctest.patch.object(FirebaseConnectionRecord, 'save')
    @asynctest.patch.object(FirebaseConnectionRecord, 'retrieve_by_connection_id')
    async def test_send_message_should_not_update_record_with_sent_time_when_firebase_fails(self, mock_retrieve, mock_save, mock_post):
        mock_retrieve.return_value = FirebaseConnectionRecord(
            connection_id=self.test_conn_id,
            sent_time=datetime_to_str(
                datetime_now() - timedelta(minutes=MAX_SEND_RATE_MINUTES + 1)),
            device_token="device-token"
        )
        mock_post.return_value = mock.Mock(status_code=400)
        await send_message(self.profile, self.test_conn_id)

        assert mock_retrieve.await_count == 1
        assert mock_post.called
        assert mock_save.await_count == 0
