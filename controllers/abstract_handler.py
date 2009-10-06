import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging, get_domain, get_application

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory

from components.sessions import Session

import urllib

################################################################################
# MainPage
class AbstractHandler(webapp.RequestHandler):
    def _get_base_url(self):
        return 'http://' + get_domain(keep_www = True)
    
    def _add_base_template_values(self, vals):
        
        vals.update( {
            'domain': self._get_base_url(),
            'path': self.request.path,
            'application_alias': get_application().get_alias(), 
        })
        
        volunteer = self.auth()
        if volunteer:
            vals['unread_message_count'] = volunteer.get_messages().filter('read =', False).filter('show_in_mailbox =', volunteer.key().id()).count()
    
    def auth(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=False)
        except:
            return None
        return volunteer