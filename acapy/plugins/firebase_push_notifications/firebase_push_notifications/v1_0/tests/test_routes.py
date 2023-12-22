from aries_cloudagent.core.event_bus import MockEventBus
from asynctest import TestCase as AsyncTestCase
from asynctest import mock

from ..routes import register_events


class TestRoutes(AsyncTestCase):

    async def test_register_events_subscribes_to_event_bus(self):
        mock_event_bus = MockEventBus()
        mock_event_bus.subscribe = mock.MagicMock()
        register_events(mock_event_bus)
        self.assertEqual(mock_event_bus.subscribe.called, True)
