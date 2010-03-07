import os, string, random
import imghdr

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.api import memcache

from controllers.abstract_handler import AbstractHandler


from models.organization import Organization

##############################################################
#Organization Page
##############################################################
class OrganizationPage(AbstractHandler):
    
    def get(self, url_data):
        self.show(url_data[1:])
        
    def show(self, org_id):
        try:
            account = self.auth(require_login = False)
        except:
            return
        
        if account:
            volunteer = account.get_user()
        else:
            volunteer = None
            
        session = self._session()
        #this is where we'd want to check to see if the volunteer is an admin of the org, and respond accordingly
#        if volunteer and volunteer.key().id() == int(volunteer_id):
#            session['redirected'] = True
#            self.redirect("/#/profile");
#            return
        
        page_organization = Organization.get_by_id(int(org_id))
        
        if not page_organization:
            self.error(404)
            return
        
        template_values = { 
              'org_of_interest': page_organization,
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'organizations', 'view_other_organization.html')
        self.response.out.write(template.render(path, template_values))

        
        
        