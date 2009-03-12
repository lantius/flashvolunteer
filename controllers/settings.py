import os
import random

from controllers._auth import Authorize
from controllers._params import Parameters

from google.appengine.ext.webapp import template
from google.appengine.api import users, images
from google.appengine.ext import webapp, db
from models import Volunteer, Neighborhood, InterestCategory, VolunteerInterestCategory

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

################################################################################
# Settings page
################################################################################
class SettingsPage(webapp.RequestHandler):

  ################################################################################
  # GET
  ################################################################################
  def get(self):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True)
    except:
      return
    self.show(user, volunteer)

  ################################################################################
  # POST
  ################################################################################
  def post(self):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(volunteer)
      self.redirect('/')
    else:  
      self.update(params, volunteer)
      self.redirect('/settings')

  ################################################################################
  # SHOW
  # TODO: this is a GET that changes the database.  danger, will robinson!
  ################################################################################
  def show(self, user, volunteer):
    if not volunteer:
      message = "Welcome newly registered volunteer"
      volunteer = Volunteer()
      volunteer.user = user
      volunteer.name = user.nickname()
      volunteer.session_id = SettingsPage.randomString(self);
      volunteer.put();
    else:
      message = "Welcome back old volunteer"
      if volunteer.home_neighborhood:
        message += " from " + volunteer.home_neighborhood.name
    
    logout_url = users.create_logout_url(self.request.uri)
    
    template_values = {
        'volunteer' : volunteer, 
        'logout_url': logout_url,
        'message': message,
        'home_neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'work_neighborhoods': NeighborhoodHelper().selected(volunteer.work_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'settings.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # UPDATE
  ################################################################################
  def update(self, params, volunteer):
    volunteer.home_neighborhood = Neighborhood.get_by_id(int(params['home_neighborhood']))
    volunteer.work_neighborhood = Neighborhood.get_by_id(int(params['work_neighborhood']))
    
    if params['avatar']:
      volunteer.avatar = params['avatar']
      
    volunteer.quote = params['quote']
    volunteer.name  = params['name']
    
    for interestcategory in InterestCategory.all():
      paramname = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      vic = VolunteerInterestCategory.gql("WHERE volunteer = :volunteer AND interestcategory = :interestcategory" ,
                          volunteer = volunteer, interestcategory = interestcategory).get()
      if params[paramname] == ['1','1'] and not vic:          
        vic = VolunteerInterestCategory(volunteer = volunteer, interestcategory = interestcategory)
        vic.put()
      elif params[paramname] == '1' and vic:
        vic.delete()
    
    volunteer.put()
      
  ################################################################################
  # DELETE
  ################################################################################
  def delete(self, volunteer):
    # Remove followers relationship
    followers = volunteer.volunteerfollowers;
    for f in followers:
      f.delete()

    # Remove following relationship
    following = volunteer.volunteerfollowing;
    for f in following:
      f.delete()
  
    # Remove volunteer interest categories
    interests = volunteer.volunteerinterestcategories;
    for interest in interests:
      interest.delete()

    # Remove events you've volunteered for
    evs = volunteer.eventvolunteers
    for ev in evs:
      ev.delete()

    # Finally remove the volunteer
    volunteer.delete()
  
  #TODO: Optimize random string generation
  def randomString(self):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_string = ''
    for count in xrange(1,64):
      random_string += random.sample(alphabet,1)[0]
        
    return random_string;
 