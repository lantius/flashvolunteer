from google.appengine.api import urlfetch
import urllib, os, logging

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template


from django.utils import simplejson
from google.appengine.api import urlfetch

from utils.applications.operations import synchronize_apps
from google.appengine.ext import deferred


from models.auth.account import Account
        
    
class SyncApplication(AbstractHandler):

    def get(self):
        try:
            account = self.auth(require_login = True, require_admin = True)
        except:
            return

        template_values = {
            'volunteer': account.get_user(),
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'sync_application.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    def post(self):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   

        deferred.defer(synchronize_apps)
        
        self.redirect('/admin')
