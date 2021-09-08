import anymarkup

from os import getenv
from logging import getLogger

from celery import Celery
from fedora_messaging import config
from fedora_messaging.message import Message

from ucho.rules_engine import evaluate_rules
from ucho.utils import UchoError, pretty_dict


config.conf.setup_logging()

logger = getLogger(__name__)

GITHUB_TOPICS = {
    "org.fedoraproject.prod.github.push",
}


class Celerize:
    """
    Create celery tasks according to given mapping file and trigger_message shared function, which should
    contain a message bus event.
    """

    def __init__(self, config_map_file):
        self.celerize_config = anymarkup.parse_file(config_map_file)
        self._celery_app = None

    @property
    def celery_app(self):
        if not self._celery_app:
            if getenv("REDIS_SERVICE_HOST"):
                host = getenv("REDIS_SERVICE_HOST")
                port = getenv("REDIS_SERVICE_PORT", "6379")
                db = getenv("REDIS_SERVICE_DB", "0")
                broker_url = f"redis://{host}:{port}/{db}"
            else:
                raise ValueError("Celery broker not configured")
            self._celery_app = Celery(broker=broker_url)
            logger.info(f"Celery uses {broker_url}")
        return self._celery_app

    def fedora_messaging_callback(self, message: Message):
        if message.topic not in GITHUB_TOPICS:
            logger.info(f"Message {message.topic} not in {GITHUB_TOPICS}.")
            return
        message.body["topic"] = message.topic
        self.execute(message)

    def execute(self, message: Message):
        if not message.body:
            raise UchoError("no message passed to the module")

        if "topic" not in message.body:
            raise UchoError("topic key not found in trigger message")

        topic = message.body["topic"]
        if topic not in self.celerize_config:
            logger.info("no config found for topic '{}'".format(topic))
            return
        # create routes to all task queues that could be used
        task_routes = {
            k: v
            for rule in self.celerize_config[topic]
            for k, v in rule.get("routes", {}).items()
        }
        if not task_routes:
            logger.info("no task->queue routes in topic %s", topic)
            return
        logger.debug(f"adding task routes {pretty_dict(task_routes)}")
        self.celery_app.conf.update(task_routes=task_routes)

        tasks_to_send = set()
        for rule in self.celerize_config[topic]:
            logger.debug(f"processing rule - {pretty_dict(rule)}")

            context = {
                "message": message.body,
            }

            result = evaluate_rules(rule.get("rule"), context=context)
            if not result:
                logger.debug("message received: %s", pretty_dict(message.body))
                logger.debug("rule {!r} does not match, moving on".format(rule["rule"]))
                continue
            for task in rule.get("routes", {}).keys():
                logger.debug("message received: %s", pretty_dict(message.body))
                logger.info(
                    "new task '{}' triggered by message on topic '{}'".format(
                        task, topic
                    )
                )
                tasks_to_send.add(task)

        for task in tasks_to_send:
            logger.info(f"Task sent to Celery is: {task}. ")
            self.celery_app.send_task(name=task, kwargs={"message": message.body})
