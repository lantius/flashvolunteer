import os, logging

from google.appengine.ext import webapp

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory
from models.application import Application


from controllers.abstract_handler import AbstractHandler

class AddApplications(AbstractHandler):

    def get(self):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   