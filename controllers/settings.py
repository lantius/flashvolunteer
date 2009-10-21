import os, logging

from controllers._auth import Authorize
from controllers._params import Parameters

from google.appengine.ext.webapp import template
from google.appengine.api import users, images, memcache
from google.appengine.ext import webapp, db

from google.appengine.api.urlfetch import fetch

from models.volunteer import Volunteer
from models.interestcategory import InterestCategory
from models.volunteerinterestcategory import VolunteerInterestCategory
from models.messages import MessageType, MessagePropagationType

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper
from components.sessions import Session

from controllers.abstract_handler import AbstractHandler

from controllers._utils import send_message
from components.message_text import type3

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
        
        logging.info('beginning settings')
        if volunteer:
            self.edit(volunteer)
        else:
            logging.info('create new vol')
            volunteer = Volunteer()
            volunteer.error.clear()
            self.new(volunteer)
        
        session = Session()
        if volunteer and \
          volunteer.avatar is None and \
          session['auth_domain'] == 'Facebook':

            try:
                import imghdr
            
                img = fetch(url = session['login_info']['photo']).content   
                content_type = imghdr.what(None, img)
                if not content_type:
                  return
            
                volunteer.avatar_type = 'image/' + content_type
                volunteer.avatar = img
                volunteer.put()          
            except:
                pass
              
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
          self.redirect('/')
          
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
          'message_propagation_types' : MessagePropagationType.all(),
          'message_types': MessageType.all().filter('in_settings =', True).order('order')
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
      
      params = {'name': volunteer.name} 
              
          
      send_message(to = [volunteer], 
                   subject = type3.subject%params,
                   body = type3.body%params,
                   type= MessageType.all().filter('name =', 'welcome').get(), 
                   immediate = True)
      
      
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
        if memcache.get('%s_rec_events'%volunteer.key().id()):
            memcache.delete('%s_rec_events'%volunteer.key().id())
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

      # Remove your message preferences
      prefs = volunteer.message_preferences;
      for pref in prefs:
        pref.delete()
            
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