from google.appengine.ext import db
from models.neighborhood import Neighborhood
from models.abstractuser import AbstractUser

from google.appengine.api import memcache
from inspect import stack

################################################################################
# Volunteer
class Volunteer(AbstractUser):

    home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
    work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')
    
    privacy__event_attendance = db.StringProperty(default='everyone')

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
    
    def friends(self):  
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [vf.followed for vf in self.following.filter('mutual =', True).order('__key__')]
            memcache.set(key, result, 1000)
                    
        return result 

    def followers_only(self):   
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [vf.follower for vf in self.followers.filter('mutual =', False).order('__key__')]
            memcache.set(key, result, 1000)
                    
        return result 
    
    def following_only(self):
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [vf.followed for vf in self.following.filter('mutual =', False).order('__key__')]
            memcache.set(key, result, 1000)
                
        return result 
    
    def following_all(self):   #returns a generator of account objects
        method = stack()[0][3]
        memkey = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(memkey)
        if not result:
            result = [vf.followed for vf in self.following]
            memcache.set(memkey, result, 1000)
        
        return result 
    
    def event_access(self, volunteer):
        if not volunteer: return False
        if self.privacy__event_attendance == 'everyone': return True
        return self.privacy__event_attendance == 'friends' and self.following.filter('followed =', volunteer).get()

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
        method = stack()[0][3]
        key = self.__class__.__name__ + method + str(self.key().id())
        result = memcache.get(key)
        if not result:
            result = [vic.interestcategory for vic in self.user_interests]
            memcache.set(key, result, 1000)
                    
        return result 
    
