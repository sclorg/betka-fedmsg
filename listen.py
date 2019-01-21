#!/usr/bin/python3
import logging
import sys
from ucho.fedmsg_listener import execute_fedmsg_receiver

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] %(message)s',datefmt='%H:%M:%S')
address=f"org.fedoraproject.prod.github"
endpoint='tcp://hub.fedoraproject.org:9940'
logging.info(f"Using address {address}")
execute_fedmsg_receiver(address, endpoint)
