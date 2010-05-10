from google.appengine.ext import db
from models.neighborhood import Neighborhood
from models.abstractuser import AbstractUser

from google.appengine.api import memcache
from models.auth.account import Account
    
################################################################################
# Volunteer
class Volunteer(AbstractUser):

    home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
    work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')
    
    privacy__event_attendance = db.StringProperty(default='everyone')
    account = db.ReferenceProperty(Account, collection_name = 'vol_user')

    def validate(self, params):
      
        # Not verifying these updates
        if 'home_neighborhood' in params:
            if params['home_neighborhood'] == 'None':
                self.home_neighborhood = None;
            else:
                self.home_neighborhood = Neighborhood.get_by_id(int(params['home_neighborhood']))
        
        if 'work_neighborhood' in params:
            if params['work_neighborhood'] == 'None':
                self.work_neighborhood = None;
            else:
                self.work_neighborhood = Neighborhood.get_by_id(int(params['work_neighborhood']))
            
            #Interest Categories updates happen in the controller
        
        if 'privacy__event_attendance' in params and self.privacy__event_attendance != params['privacy__event_attendance']:
            self.privacy__event_attendance = params['privacy__event_attendance']
        
        return AbstractUser.validate(self, params)
    
    def url(self):
        return '/volunteers/' + str(self.key().id())
    
    def friends(self):  #returns a generator of Volunteer objects
        return [vf.follows.get_user() for vf in self.account.following.filter('mutual =', True).order('__key__')]

    def followers_only(self):   #returns a generator of Volunteer objects
        return (vf.follower.get_user() for vf in self.account.followers.filter('mutual =', False).order('__key__'))
    
    def following_only(self):   #returns a generator of Volunteer objects
        return (vf.follows.get_user() for vf in self.account.following.filter('mutual =', False).order('__key__'))

    def following(self, key = None, limit = None):   #returns a generator of account objects
        qry = self.account.following.order('__key__')
        if key: 
            qry = qry.filter('__key__ >=', key)
        if limit:
            return (vf.follows.get_user() for vf in qry.fetch(limit))
        else:
            return (vf.follows.get_user() for vf in qry)

    def event_access(self, account):
        if not account: return False
        if self.privacy__event_attendance == 'everyone': return True
        return self.privacy__event_attendance == 'friends' and self.account.following.filter('follows =', account).get()

    def recommended_events(self, application, session):
        #TODO make more efficient
        recommended_events = session.get('%s_rec_events'%self.key().id(), None)
        if recommended_events:
            return recommended_events
    
        vol_events = dict([(ev.event.key().id(),1) for ev in self.events_future()])
        vol_events.update(dict([(ev.event.key().id(),1) for ev in self.events_coordinating()]))
    
        neighborhoods = {}
        if(self.work_neighborhood):
            neighborhoods[self.work_neighborhood.key().id()] = 1
        if(self.home_neighborhood):
            neighborhoods[self.home_neighborhood.key().id()] = 1
        
        vol_interests = set([ic.key().id() for ic in self.interestcategories()])
        vol_interest_map = dict([(ic.key().id(),ic) for ic in self.interestcategories()])
                
        upcoming_events = application.upcoming_events()
        
        recommended_events = []
        reason_recommended = {}
        
        for e in upcoming_events:
            reason = []
            # recommend non rsvp'd events
            if e.key().id() in vol_events: continue
        
            #recommend events in home or work neighborhood          
            if self.home_neighborhood and self.home_neighborhood.key().id() == e.neighborhood.key().id():
                reason.append('Live nearby')
            if self.work_neighborhood and self.work_neighborhood.key().id() == e.neighborhood.key().id() and \
               self.work_neighborhood.key().id() != self.home_neighborhood.key().id():
                reason.append('Work nearby')
            
            common_interests = vol_interests.intersection(
                       set([ic.key().id() for ic in e.interestcategories()]))
    
            for ic_id in common_interests:
                reason.append('Category: %s'%vol_interest_map[ic_id])
            
            if len(reason) > 0:
                recommended_events.append(e)
            
        #########
        session['%s_rec_events'%self.key().id()] = recommended_events
        return recommended_events

    def interestcategories(self):
        return (vic.interestcategory for vic in self.account.user_interests)

###### DEPRECATED; USE ACCOUNT'S METHODS INSTEAD #############

    def get_first_name(self):
        return self.get_first_name()
    
    def get_last_name(self):
        return self.account.get_last_name()
        
    def get_name(self):
        return self.account.get_name()
    
    def get_email(self):
        return self.account.get_email()
    
    def _get_message_pref(self, type):
        return self._get_message_pref(type)

