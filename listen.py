#!/usr/bin/python3
import logging
import sys
from ucho.fedmsg_listener import listen_from_fedora_messaging

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
logging.info("Start listening on Fedora Messaging.")
listen_from_fedora_messaging()
