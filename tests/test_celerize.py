"""Test Celerize class"""
from pathlib import Path
import anymarkup
import os

from flexmock import flexmock

from fedora_messaging.message import Message
from ucho.celerize import Celerize


CELERY_MAP_PATH = Path(__file__).parent / "data/test-celery-map.yaml"


class TestCelerize(object):
    """Test Celerize class"""

    def setup_method(self):
        os.environ["REDIS_SERVICE_HOST"] = "localhost"
        self.celerize = Celerize(CELERY_MAP_PATH)
        self.message = Message()

    def test_celerize_config(self):
        assert self.celerize.celerize_config == anymarkup.parse_file(CELERY_MAP_PATH)

    def test_rule_not_matching(self):
        assert self.celerize.celery_app
        flexmock(self.celerize.celery_app.conf).should_receive(
            "update"
        ).once().and_return()
        flexmock(self.celerize.celery_app).should_receive("send_task").never()
        self.message.body = {
            "topic": "event.failing.rule",
            "numcommits": "0",
            "branch": "rhel-8.0.0",
        }
        self.celerize.execute(self.message)

    def test_task_routes_loaded(self):
        assert self.celerize.celery_app
        flexmock(self.celerize.celery_app.conf).should_receive(
            "update"
        ).once().and_return()
        flexmock(self.celerize.celery_app).should_receive("send_task").times(
            3
        ).and_return()
        self.message.body = {"topic": "some.new.event", "action": "created"}
        self.celerize.execute(self.message)

    def test_no_rule(self):
        assert self.celerize.celery_app
        flexmock(self.celerize.celery_app.conf).should_receive(
            "update"
        ).once().and_return()
        flexmock(self.celerize.celery_app).should_receive("send_task").and_return()
        self.message.body = {"topic": "event.no.rule"}
        self.celerize.execute(self.message)
