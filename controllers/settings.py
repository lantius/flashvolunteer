import os, logging


from google.appengine.ext.webapp import template
from google.appengine.api import users, images, memcache
from google.appengine.ext import webapp, db

from models.interestcategory import InterestCategory
from models.interest import Interest
from models.messages import MessageType, MessagePropagationType


from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

from controllers.abstract_handler import AbstractHandler

################################################################################
# Settings page
################################################################################
class SettingsPage(AbstractHandler):
    LIMIT = 2
    ################################################################################
    # GET
    ################################################################################
    def get(self, volunteer = None):  
        if self.request.path.find('delete') > -1:
            self.confirm_delete()
        else:
            self.show(volunteer = volunteer)
        
    def show(self, volunteer):    
        if not volunteer:
            try:
                volunteer = self.auth(require_login=True)
            except:
                return

        (future_events, past_events, 
         events_coordinating, past_events_coordinated) = volunteer.get_activities(SettingsPage.LIMIT)
        
        (future_events_cnt, past_events_cnt, 
         events_coordinating_cnt, past_events_coordinated_cnt) = volunteer.get_activities()

        template_values = {
            'volunteer' : volunteer, 
            'home_neighborhoods': NeighborhoodHelper().selected(self.get_application(),volunteer.home_neighborhood),
            'work_neighborhoods': NeighborhoodHelper().selected(self.get_application(),volunteer.work_neighborhood),
            'interestcategories' : InterestCategoryHelper().selected(volunteer),
            'message_propagation_types' : MessagePropagationType.all(),
            'message_types': MessageType.all().filter('in_settings =', True).order('order'),

            'past_events': past_events,
            'future_events': future_events,
            'past_events_coordinated': past_events_coordinated,
            'events_coordinating': events_coordinating,

            'past_events_cnt': past_events_cnt,
            'future_events_cnt': future_events_cnt,
            'past_events_coordinated_cnt': past_events_coordinated_cnt,
            'events_coordinating_cnt': events_coordinating_cnt,
            
            'user_of_interest': volunteer,
            'event_access': True
            
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'settings.html')
        self.response.out.write(template.render(path, template_values))

    ################################################################################
    # POST
    ################################################################################
    def post(self):
        try:
            volunteer = self.auth(require_login = True)
        except:
            return
          
        params = self.parameterize() 
        session = self._session()      
        
        if 'is_delete' in params and params['is_delete'] == 'true':     
            if 'confirm_delete' in params and params['confirm_delete'] == 'true':
                self.delete(volunteer)
                session.flush()
                self.redirect('/#/logout')
        else:  
            if self.update(params, volunteer):
                self.add_notification_message('Your settings have been updated.')
                self.redirect('/#/profile')
            else:
                self.add_notification_message('Oops! Your messages could not be saved.')

    ################################################################################
    # UPDATE
    def update(self, params, volunteer):

        valid_entry = volunteer.validate(params) 
      
        for interestcategory in InterestCategory.all():
            param_name = 'interestcategory[' + str(interestcategory.key().id()) + ']'
            if not param_name in params:
                continue
            vic = volunteer.user_interests.filter('interestcategory =', interestcategory).get()
            if params[param_name] == ['1','1'] and not vic:          
                vic = Interest(user = volunteer, interestcategory = interestcategory)
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
        #TODO: check if batch deletes work and use them if so
        
        # Remove followers relationship
        followers = volunteer.followers
        for f in followers:
            f.delete()
        
        # Remove following relationship
        following = volunteer.following
        for f in following:
            f.delete()
        
        # Remove volunteer interest categories
        interests = volunteer.user_interests
        for interest in interests:
            interest.delete()
        
        # Remove your message preferences
        prefs = volunteer.message_preferences
        for pref in prefs:
            pref.delete()
            
        # Remove message receipts
        mrs = volunteer.incoming_messages
        for mr in mrs:
            mr.delete()
              
        # Remove events you've volunteered for
        evs = volunteer.eventvolunteers
        for ev in evs:
            ev.delete()
        
        # Finally remove the volunteer
        for auth in volunteer.auth_methods:
            auth.delete()
            
        volunteer.delete()
        
    
    ################################################################################
    # CONFIRM_DELETE
    def confirm_delete(self):
        try:
            volunteer = self.auth(require_login = True)
        except:
            return

        template_values = {
            'volunteer' : volunteer, 
          }
        self._add_base_template_values(vals = template_values)
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'confirm_delete.html')
        self.response.out.write(template.render(path, template_values))