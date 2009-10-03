from components.sessions import Session
from controllers._utils import get_server, get_application
from controllers.applications.operations import add_applications
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache, mail
from google.appengine.ext import webapp

import os, logging

from models.message import Message
from components.time_zones import now

class MessageDispatcher(AbstractHandler):

    def get(self):
        messages_to_send = Message.all().filter('sent =', False).filter('trigger <', now())

        for message in messages_to_send:
            message.send()        