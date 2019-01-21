import os
import celery
import logging
import anymarkup
from ucho.rules_engine import evaluate_rules
from ucho.utils import UchoError, pretty_dict


class Celerize:
    """
    Create celery tasks according to given mapping file and trigger_message shared function, which should
    contain a message bus event.
    """

    def __init__(self, config_map_file):
        self.celerize_config = anymarkup.parse_file(config_map_file)
        self._celery = celery.Celery(broker=os.environ.get('REDIS_BROKER'),
                                     backend=os.environ.get('REDIS_BACKEND'))

    def execute(self, message):
        if not message:
            raise UchoError('no message passed to the module')

        if 'topic' not in message:
            raise UchoError('topic key not found in trigger message')

        topic = message['topic']
        if topic not in self.celerize_config:
            logging.info("no config found for topic '{}'".format(topic))
            return
        # create routes to all task queues that could be used
        task_routes = {k: v for rule in self.celerize_config[topic]
                       for k, v in rule.get('routes', {}).items()}
        if not task_routes:
            logging.info('no task->queue routes in topic %s', topic)
            return
        logging.debug(f"adding task routes {pretty_dict(task_routes)}")
        self._celery.conf.update(task_routes=task_routes)

        tasks_to_send = set()
        for rule in self.celerize_config[topic]:
            logging.debug(f"processing rule - {pretty_dict(rule)}")

            context = {
                'message': message['msg'],
            }

            result = evaluate_rules(rule.get('rule'), context=context)
            if not result:
                logging.debug("message received: %s", pretty_dict(message))
                logging.info('rule {!r} does not match, moving on'.format(rule['rule']))
                continue

            for task in rule.get('routes', {}).keys():
                logging.debug("message received: %s", pretty_dict(message))
                logging.info("new task '{}' triggered by message on topic '{}'".format(task, topic))
                tasks_to_send.add(task)

        for task in tasks_to_send:
            self._celery.send_task(task, kwargs={'message': message})
