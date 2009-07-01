import os

from controllers._auth import Authorize
from controllers._params import Parameters

from google.appengine.ext.webapp import template
from google.appengine.api import users, images
from google.appengine.ext import webapp, db

from models.volunteer import *
from models.neighborhood import *
from models.interestcategory import *
from models.volunteerinterestcategory import *

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
      volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return
    if volunteer:
      self.edit(volunteer)
    else:
      volunteer = Volunteer()
      volunteer.error.clear()
      self.new(volunteer)

  ################################################################################
  # POST
  ################################################################################
  def post(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return

    params = Parameters.parameterize(self.request)
    if not volunteer:
      if self.create(params):
        self.redirect('/')
        
    else:
      if 'is_delete' in params and params['is_delete'] == 'true':
        self.delete(volunteer)
        self.redirect('/')
      else:  
        if self.update(params, volunteer):
          self.redirect('/settings')
        

  ################################################################################
  # EDIT
  def edit(self, volunteer):
    template_values = {
        'volunteer' : volunteer, 
        'home_neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'work_neighborhoods': NeighborhoodHelper().selected(volunteer.work_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'settings.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # NEW
  def new(self, volunteer):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    template_values = {
        'default_name' : user.nickname(),
        'volunteer' :  volunteer,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'create.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # CREATE
  def create(self, params):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    volunteer = Volunteer()
    volunteer.user = user
    
    if not volunteer.validate(params):
      self.new(volunteer)
      return False
      
    volunteer.put()
    return True
    
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    
    if not volunteer.validate(params):
      self.edit(volunteer)
      return False
    
    for interestcategory in InterestCategory.all():
      param_name = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      if not param_name in params:
        continue
      vic = VolunteerInterestCategory.gql("WHERE volunteer = :volunteer AND interestcategory = :interestcategory" ,
                          volunteer = volunteer, interestcategory = interestcategory).get()
      if params[param_name] == ['1','1'] and not vic:          
        vic = VolunteerInterestCategory(volunteer = volunteer, interestcategory = interestcategory)
        vic.put()
      elif params[param_name] == '1' and vic:
        vic.delete()
  
    
    volunteer.put()
    return True
      
  ################################################################################
  # DELETE
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
