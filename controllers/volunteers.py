import os, string, random
import imghdr, logging

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.db import Key
from google.appengine.api import memcache

from models.volunteer import Volunteer
from models.volunteerfollower import VolunteerFollower
from models.neighborhood import Neighborhood

from controllers.abstract_handler import AbstractHandler

from controllers._helpers import NeighborhoodHelper


################################################################################
# Volunteers page
class VolunteersPage(AbstractHandler):
    LIMIT = 12
    ################################################################################
    # GET
    def get(self, url_data):
    
        if url_data:
            if '/search' == url_data:
                params = self.parameterize() 
                self.search(params)
            else:
                self.show(url_data[1:])        
        else:
            self.list() 
    
    ################################################################################
    # SHOW
    def show(self, volunteer_id):
        try:
            volunteer = self.auth(require_login=False)
        except:
            return
        
        session = self._session()
        if volunteer and volunteer.key().id() == int(volunteer_id):
            session['redirected'] = True
            self.redirect("/#/profile");
            return
        
        #TODO: if application instances are closed, do not allow people to view
        
        page_volunteer = Volunteer.get_by_id(int(volunteer_id))
        
        if not page_volunteer:
            self.error(404)
            return
        
        if volunteer:
            volunteerfollower = volunteer.following.filter('followed =', page_volunteer).get()                  
            volunteerfollowing = volunteer.followers.filter('follower =', page_volunteer).get()
                                                    
            event_access = page_volunteer.event_access(volunteer = volunteer) 
        else:
            event_access = False
            volunteerfollower = None
            volunteerfollowing = None
                          
        #vhours = sum([ev.hours for ev in page_volunteer.eventvolunteers if ev.hours])
        
        (future_events, past_events, 
         events_coordinating, past_events_coordinated) = page_volunteer.get_activities(VolunteersPage.LIMIT)
        
        (future_events_cnt, past_events_cnt, 
         events_coordinating_cnt, past_events_coordinated_cnt) = page_volunteer.get_activities()
        
        friends = page_volunteer.friends()
        if len(friends) > 5:
            friends = random.sample(friends, 5)
        template_values = { 
              'eventvolunteer': page_volunteer.eventvolunteers, 
              'volunteerfollower' : volunteerfollower,
              'volunteerfollowing' : volunteerfollowing,
              'page_volunteer': page_volunteer,
              'volunteer' : volunteer,
              'event_access': event_access,
        
              'past_events': past_events,
              'future_events': future_events,
              'past_events_coordinated': past_events_coordinated,
              'events_coordinating': events_coordinating,
        
              'past_events_cnt': past_events_cnt,
              'future_events_cnt': future_events_cnt,
              'past_events_coordinated_cnt': past_events_coordinated_cnt,
              'events_coordinating_cnt': events_coordinating_cnt,
            
              'user_of_interest': page_volunteer,
              'friends': friends,
              'neighborhoods': NeighborhoodHelper().selected(self.get_application(),page_volunteer.home_neighborhood),

        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'view_other_volunteer.html')
        self.response.out.write(template.render(path, template_values))
    
    ################################################################################
    # SEARCH
    def search(self, params):
        try:
            volunteer = self.auth(require_login=False)
        except:
            return
        
        (name, email, neighborhood, volunteers, next, prev)  = self.do_search(params)
        template_values = { 
          'neighborhood' : neighborhood,
          'email' : email,
          'name' : name,
          'volunteers' : volunteers,
          'volunteer' : volunteer,
          'next': next,
          'prev': prev,
          'url': '/volunteers/search'
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'volunteers_search.html')
        self.response.out.write(template.render(path, template_values))

    def do_search(self, params):
        SEARCH_LIST = 12
        session = self._session()
        application = self.get_application()
        volunteers_query = Volunteer.all().filter('applications =', application.key().id()).order('__key__')
        
        bookmark = self.request.get("bookmark", None)
        if bookmark and bookmark != '-':
            volunteers_query = volunteers_query.filter('__key__ >=', Key(encoded=bookmark))
            
            trace = session.get('volunteers_search_prev', None)
            if not trace or trace == []:
                session['volunteers_search_prev'] = [bookmark]
                prev = '-'
            else:                
                if 'back' in params and params['back'] == '1':
                    prev = trace.pop() 
                    while prev >= bookmark:
                        try:
                            prev = trace.pop()
                        except: 
                            prev = '-'
                            break
                else:
                    prev = trace[-1]
                    trace.append(bookmark)
                    
                session['volunteers_search_prev'] = trace
                
        else:
            if 'volunteers_search_prev' in session:
                del session['volunteers_search_prev']
                    
            prev = ''
        
        neighborhood = None
        name = None
        email = None
        
        if 'neighborhood' in params and params['neighborhood']:
          try:
            neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
            volunteers_query.filter('home_neighborhood =', neighborhood)
          except:
            pass
        
        if 'name' in params and params['name']:
          try:
            name = params['name']
            volunteers_query.filter('name =', name)
          except:
            pass
        
#        if 'email' in params and params['email']:
#          try:
#            email = params['email'] 
#            volunteers_query.filter('preferred_email =', email)
#          except:
#            pass
        
        volunteers = volunteers_query.fetch(limit = SEARCH_LIST + 1)

        if len(volunteers) == SEARCH_LIST+1:
            next = volunteers[-1].key()
            volunteers = volunteers[:SEARCH_LIST]
        else:
            next = None
            
        return (name, email, neighborhood, volunteers, next, prev)
    
    
################################################################################
# FollowVolunteer

from utils.message_text import type2
from models.messages import MessageType

class FollowVolunteer(AbstractHandler):
    
    ################################################################################
    # POST
    def post(self, url_data):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        to_follow = Volunteer.get_by_id(int(url_data))
        
        if to_follow:
            volunteerfollower = to_follow.followers.filter('follower =', volunteer).get()
            
            mutual = to_follow.following.filter('followed =', volunteer).get()
            
            if self.request.get('delete') and self.request.get('delete') == "true":
                if volunteerfollower:
                    volunteerfollower.delete()
                    if mutual:
                        mutual.mutual = False
                        mutual.put()
            else:
                if not volunteerfollower:
                    volunteerfollower = VolunteerFollower(followed=to_follow, follower=volunteer, mutual = mutual is not None)
                    volunteerfollower.put()
                    params = self.get_message_params(adder = volunteer, volunteer = to_follow)
                    subject = type2.subject%params
                    body = type2.body%params
                    self.send_message( 
                        to = [to_follow], 
                        subject = subject, 
                        body = body, 
                        type = MessageType.all().filter('name =', 'added_to_team').get(),
                        domain = self.get_domain())   
        
        #self.redirect('/volunteers/' + url_data)
        #self.redirect(self.request.referrer)
        
        return
    
    def get_message_params(self,adder, volunteer):
        params = {
            'adder_name': adder.name,
            'vol_name': volunteer.name,
            'adder_url': '%s%s'%(self._get_base_url(), adder.url()),
            'vol_team_url': '%s%s'%(self._get_base_url(), volunteer.url()), 
            'reciprocation':''
        }
        
        reciprocal = adder.following.filter('volunteer =', volunteer).get()
        if reciprocal:
            params['reciprocation'] = ' also'
        
        return params
    
################################################################################
# VolunteerAvatar
class VolunteerAvatar(AbstractHandler):
    ################################################################################
    # GET
    def get(self, url_data):
        volunteer = Volunteer.get_by_id(int(url_data))

        if volunteer.avatar:
            self.response.headers['Content-Type'] = str(volunteer.avatar_type)
            self.response.out.write(volunteer.avatar)
        else:
            self.error(404)
    
    ################################################################################
    # POST
    def post(self):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
          
        params = self.parameterize() 
        
        if 'delete_avatar' in params and params['delete_avatar'] == 'true':
            self.delete(volunteer)
        else:
            self.update(params, volunteer)
        
        self.redirect('/#/settings')
    
    ################################################################################
    # DELETE
    def delete(self, volunteer):
        volunteer.avatar = None
        volunteer.put()
      
    ################################################################################
    # UPDATE
    def update(self, params, volunteer):
        session = self._session()
        if 'avatar' in params and params['avatar']:
            if len(params['avatar']) > 50 * 2**10:
                self.add_notification_message('Sorry! That file is too big. Please choose one under 50kb.')
                return
          
        content_type = imghdr.what(None, params['avatar'])
        if not content_type:
            self.add_notification_message('Sorry! We cannot read that type of file.')
            return
    
        volunteer.avatar_type = 'image/' + content_type
        volunteer.avatar = params['avatar']
        volunteer.put()

