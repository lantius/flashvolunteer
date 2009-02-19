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
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

    # Remove followers relationship
    followers = volunteer.followers();
    for f in followers:
      f.delete()

    # Remove following relatoinship
    following = volunteer.following();
    for f in following:
      f.delete()
    
    # Remove interest categories
    interests = volunteer.interestcategories();
    for interest in interests:
      interest.delete()

    # Remove events you've volunteered for
    evs = volunteer.eventvolunteers
    for ev in evs:
      ev.delete()

    # Finally remove the volunteer
    volunteer.delete()
    
	#We need to put a better page here
    self.redirect('/')

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
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True)
    except:
      return

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
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

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
    