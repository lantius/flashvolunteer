import os, logging


from google.appengine.ext.webapp import template
from google.appengine.api import users, images, memcache
from google.appengine.ext import webapp, db

from google.appengine.api.urlfetch import fetch

from models.volunteer import Volunteer
from models.interestcategory import InterestCategory
from models.interest import Interest
from models.messages import MessageType, MessagePropagationType

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
    def get(self, volunteer = None):      
        if not volunteer:
            try:
                account = self.auth(require_login=True)
            except:
                return

        volunteer = account.get_user()
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
    # POST
    ################################################################################
    def post(self):
      try:
          account = self.auth(require_login = True)
      except:
          return
        
      params = self.parameterize() 
      session = Session()      

      if 'is_delete' in params and params['is_delete'] == 'true':     
          if 'confirm_delete' in params and params['confirm_delete'] == 'true':
              self.delete(account)
              self.redirect('/')
          else:
              self.confirm_delete(account)
      else:  
          if self.update(params, account):
              self.redirect('/profile')

    ################################################################################
    # UPDATE
    def update(self, params, account):

        user = account.get_user()
        valid_entry = account.validate(params) 
        valid_entry = user.validate(params) and valid_entry
      
        for interestcategory in InterestCategory.all():
            param_name = 'interestcategory[' + str(interestcategory.key().id()) + ']'
            if not param_name in params:
                continue
            vic = account.user_interests.filter('interestcategory =', interestcategory).get()
            if params[param_name] == ['1','1'] and not vic:          
                vic = Interest(account = account, interestcategory = interestcategory)
                vic.put()
            elif params[param_name] == '1' and vic:
                vic.delete()
    
        user.put()
        account.put()
        if memcache.get('%s_rec_events'%user.key().id()):
            memcache.delete('%s_rec_events'%user.key().id())
        return True
        
    ################################################################################
    # DELETE
    def delete(self, account):
      # Remove followers relationship
      followers = account.followers
      for f in followers:
        f.delete()
    
      # Remove following relationship
      following = account.following
      for f in following:
        f.delete()
    
      # Remove volunteer interest categories
      interests = account.user_interests
      for interest in interests:
        interest.delete()

      # Remove your message preferences
      prefs = account.message_preferences
      for pref in prefs:
        pref.delete()
            
      # Remove events you've volunteered for
      evs = account.eventvolunteers
      for ev in evs:
        ev.delete()
    
      # Finally remove the volunteer
      account.get_user().delete()
      account.delete()
      
      self.redirect('/')
    
    ################################################################################
    # CONFIRM_DELETE
    def confirm_delete(self, account):
      #requires a POST from the settings page, so volunteer can be assumed.
      template_values = {
          'volunteer' : account.get_user(), 
        }
      self._add_base_template_values(vals = template_values)
      path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'confirm_delete.html')
      self.response.out.write(template.render(path, template_values))