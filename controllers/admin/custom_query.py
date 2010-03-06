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

from django.utils import simplejson
import datetime

class CustomQueryHandler(AbstractHandler):

    def get(self):
        try:
            account = self.auth(require_login = True, require_admin = True)
        except:
            return
        
        results= EventVolunteer.all().filter('isowner =',False)
        
                    
        template_values = {
            'volunteer': account.get_user(),
            'results': results,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'custom_query.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    