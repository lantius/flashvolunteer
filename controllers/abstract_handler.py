import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging, get_domain

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory

from components.sessions import Session

import urllib

################################################################################
# MainPage
class AbstractHandler(webapp.RequestHandler):
    def _add_base_template_values(self, vals):
        
        vals.update( {
            'domain': get_domain(keep_www = True),
            'path': self.request.path
        })
        