import os

from controllers._auth import Authorize
from controllers._params import Parameters

from google.appengine.ext.webapp import template
from google.appengine.api import users, images
from google.appengine.ext import webapp, db

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory
from models.volunteerinterestcategory import VolunteerInterestCategory

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper
from components.sessions import Session

from controllers.abstract_handler import AbstractHandler


################################################################################
# Settings page
################################################################################
class SettingsPage(AbstractHandler):

  ################################################################################
  # GET
  ################################################################################
  def get(self):      
    try:
      volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return
    
    
    if volunteer:
      session = Session()
      if 'redirect' in session:
        self.redirect(session['redirect'])
        del session['redirect']
        return
                
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
    session = Session()
    
    if not volunteer:
      if self.create(params):
        redirect = session.get('redirect', '/')
        if redirect in session:
            del session['redirect']
        self.redirect(redirect)
        
    else:
      if 'is_delete' in params and params['is_delete'] == 'true':     
        if 'confirm_delete' in params and params['confirm_delete'] == 'true':
          self.delete(volunteer)
          self.redirect('/')
        else:
          self.confirm_delete(volunteer)
          
      else:  
        if self.update(params, volunteer):
            self.redirect('/settings')
        

  ################################################################################
  # EDIT
  def edit(self, volunteer):
    #requires a POST from the settings page, so volunteer can be assumed.
    template_values = {
        'volunteer' : volunteer, 
        'home_neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'work_neighborhoods': NeighborhoodHelper().selected(volunteer.work_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'settings.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # NEW
  def new(self, volunteer):
    session = Session()
    user = session.get('user', None)
    
    if not user:
      self.redirect('/login')
      return

    template_values = {
        'default_name' : user.nickname(),
        'default_email': user.email(),
        'volunteer' :  volunteer
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'create.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # CREATE
  def create(self, params):
    session = Session()
    user = session.get('user', None)

    if not user:
      self.redirect('/create')
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
    
    self.redirect('/')
  
  ################################################################################
  # CONFIRM_DELETE
  def confirm_delete(self, volunteer):
    #requires a POST from the settings page, so volunteer can be assumed.
    template_values = {
        'volunteer' : volunteer, 
      }
    self._add_base_template_values(vals = template_values)
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'confirm_delete.html')
    self.response.out.write(template.render(path, template_values))