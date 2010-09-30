from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib, os, logging

from utils.misc_methods import get_neighborhood
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models.afg_opportunity import AFGOpportunity
from models.eventvolunteer import EventVolunteer
from models.volunteer import Volunteer

from django.utils import simplejson
import datetime

class CustomQueryHandler(AbstractHandler):

    def get(self):
        try:
            volunteer = self.auth(require_login = True, require_admin = True)
        except:
            return
        
        results= db.GqlQuery("SELECT * FROM Volunteer where date_added > DATETIME(2010,8,10,0,0)")
                    
        template_values = {
            'volunteer': volunteer,
            'results': results,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'custom_query.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    