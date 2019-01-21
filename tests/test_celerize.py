"""Test Celerize class"""
from pathlib import Path
import anymarkup
from flexmock import flexmock

from ucho.celerize import Celerize


CELERY_MAP_PATH = Path(__file__).parent / 'data/test-celery-map.yaml'


class TestCelerize(object):
    """Test Celerize class"""

    def setup_method(self):
        self.celerize = Celerize(CELERY_MAP_PATH)

    def test_celerize_config(self):
        assert self.celerize.celerize_config == anymarkup.parse_file(CELERY_MAP_PATH)

    def test_rule_not_matching(self):
        flexmock(self.celerize._celery.conf). \
            should_receive("update").once(). \
            and_return()
        flexmock(self.celerize._celery).\
            should_receive("send_task").never()
        message = {
            'topic': 'event.failing.rule',
            'msg': {
                "numcommits": "0",
                "branch": "rhel-8.0.0",
            }
        }
        self.celerize.execute(message)

    def test_task_routes_loaded(self):
        flexmock(self.celerize._celery.conf). \
            should_receive("update").once().\
            and_return()
        flexmock(self.celerize._celery).\
            should_receive("send_task").times(3). \
            and_return()
        message = {
            'topic': 'some.new.event',
            'msg': 'pull request'
        }
        self.celerize.execute(message)

    def test_no_rule(self):
        flexmock(self.celerize._celery.conf). \
            should_receive("update").once(). \
            and_return()
        flexmock(self.celerize._celery). \
            should_receive("send_task"). \
            and_return()
        message = {
            'topic': 'event.no.rule',
            'msg': 'Just passing'
        }
        self.celerize.execute(message)
