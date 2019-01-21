import os
import zmq
import anymarkup
import logging
from ucho.utils import pretty_dict, get_configuration_path
from ucho.celerize import Celerize


def execute_fedmsg_receiver(address, endpoint):
    celerize = Celerize(os.path.join(get_configuration_path(), 'fedmsg-celerize-map.yaml'))
    ctx = zmq.Context()
    s = ctx.socket(zmq.SUB)
    s.connect(endpoint)

    s.setsockopt(zmq.SUBSCRIBE, address.encode())

    poller = zmq.Poller()
    poller.register(s, zmq.POLLIN)

    logging.info("connected to '{}' endpoint".format(endpoint))
    while True:
        _ = poller.poll()  # This blocks until a message arrives
        topic, msg = s.recv_multipart()
        message = anymarkup.parse(msg)
        details = {
            'topic': topic.decode('utf-8'),
            'msg': message['msg']
        }

        logging.info('received message from topic: %s', topic.decode('utf-8'))
        logging.info('Message ID: %s', message.get('msg_id', 'Not Found'))
        celerize.execute(details)
