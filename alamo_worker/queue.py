# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import zmq


class ZeroMQQueue(object):
    """Zero MQ message queue client."""

    host = None
    port = None
    context = None
    zmq_socket = None

    def __init__(self, host, port, socket_type='PULL'):
        self.host = host
        self.port = port
        self.socket_type = socket_type
        self.context = zmq.Context()

    def connect(self):
        self.zmq_socket = self.context.socket(getattr(zmq, self.socket_type))
        self.zmq_socket.connect("{}:{}".format(self.host, self.port))
