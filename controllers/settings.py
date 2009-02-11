import os
import random

from controllers._auth import Authorize

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Neighborhood, InterestCategory, VolunteerInterestCategory

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

################################################################################
# Settings page
################################################################################
class DeleteVolunteerPage(webapp.RequestHandler):
  
  def get(self):
    (user, volunteer) = Authorize.login(self,True, True, '/')
    
    volunteer.delete()
    
    self.response.out.write('volunteer removed')

################################################################################
# Settings page
################################################################################
class SettingsPage(webapp.RequestHandler):
  
  #TODO: Optimize random string generation
  def randomString(self):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_string = ''
    for count in xrange(1,64):
      random_string += random.sample(alphabet,1)[0]
        
    return random_string;
        
  def get(self):
    (user, volunteer) = Authorize.login(self, requireUser=True)

    if not volunteer:
      message = "Welcome newly registered volunteer"
      volunteer = Volunteer()
      volunteer.user = user
      volunteer.session_id = SettingsPage.randomString(self);
      volunteer.put();
    else:
      message = "Welcome back old volunteer"
      if volunteer.neighborhood:
        message += " from " + volunteer.neighborhood.name
    
    logout_url = users.create_logout_url(self.request.uri)
    
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'neighborhoods': NeighborhoodHelper().selected(volunteer),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'settings.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')

    if volunteer.check_session_id(self.request.get('session_id')) and self.request.get('neighborhood'):      
      volunteer.neighborhood = Neighborhood.get_by_id(int(self.request.get('neighborhood')))
      volunteer.put()
      
      for interestcategory in InterestCategory.all():
        paramname = 'interestcategory[' + str(interestcategory.key().id()) + ']'
        vic = VolunteerInterestCategory.gql("WHERE volunteer = :volunteer AND interestcategory = :interestcategory" ,
                            volunteer = volunteer, interestcategory = interestcategory).get()
        if self.request.get_all(paramname) == ['1','1'] and not vic:          
          vic = VolunteerInterestCategory(volunteer = volunteer, interestcategory = interestcategory)
          vic.put()
        elif self.request.get_all(paramname) == ['1'] and vic:
          vic.delete()
      
      
    self.redirect('settings')
    