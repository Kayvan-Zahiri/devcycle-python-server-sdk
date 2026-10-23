import unittest

import responses
from responses.matchers import request_kwargs_matcher

from devcycle_python_sdk.api.event_client import EventAPIClient
from devcycle_python_sdk.models.event import UserEventsBatchRecord
from devcycle_python_sdk.models.user import DevCycleUser
from devcycle_python_sdk.options import DevCycleLocalOptions


class EventTimeoutTest(unittest.TestCase):
    @responses.activate
    def _check_timeout(self, timeout_ms=None):
        options = (
            DevCycleLocalOptions()
            if timeout_ms is None
            else DevCycleLocalOptions(event_request_timeout_ms=timeout_ms)
        )
        client = EventAPIClient("dvc_server_test", options)
        expected_seconds = (10000 if timeout_ms is None else timeout_ms) / 1000.0
        responses.add(
            responses.POST,
            client.batch_url,
            json={"message": "received"},
            match=[request_kwargs_matcher({"timeout": expected_seconds})],
        )
        batch = [
            UserEventsBatchRecord(user=DevCycleUser(user_id="test-user"), events=[])
        ]
        try:
            self.assertEqual(client.publish_events(batch), "received")
            self.assertEqual(len(responses.calls), 1)
        finally:
            client.session.close()

    def test_default_timeout(self):
        self._check_timeout()

    def test_one_millisecond_timeout(self):
        self._check_timeout(1)

    def test_subsecond_timeout(self):
        self._check_timeout(250)

    def test_fractional_second_timeout(self):
        self._check_timeout(1250)
