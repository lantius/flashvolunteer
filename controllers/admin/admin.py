import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import Volunteer

from controllers._params import Parameters
from controllers._auth import Authorize

from controllers.abstract_handler import AbstractHandler

################################################################################
# Admin
################################################################################
class AdminPage(AbstractHandler):
  
  ################################################################################
  # GET
  def get(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True)
    except:
      return

    self.list(volunteer)

  ################################################################################
  # POST
  def post(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True)
    except:
      return
    
    params = Parameters.parameterize(self.request)
    self.update(params, volunteer)
    self.redirect("/admin")

  ################################################################################
  # LIST
  def list(self, volunteer):
    
    volunteers = Volunteer.gql("WHERE create_rights=true")
    
    template_values = {
      'volunteers' : volunteers,
      'volunteer' : volunteer,
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'admin', 'list.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    if 'email' in params and params['email'] and 'create_rights' in params and params['create_rights']:
      volunteers = Volunteer.all()
      for volunteer in Volunteer.all():
        if volunteer.user.email() == params['email']:
          if 'true' == params['create_rights']:
            volunteer.create_rights = True
          else:
            volunteer.create_rights = False
          volunteer.put()
      