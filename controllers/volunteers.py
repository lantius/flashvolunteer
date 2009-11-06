import os, string
import imghdr

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._utils import get_application

from controllers._params import Parameters

from models.volunteer import Volunteer
from models.volunteerfollower import VolunteerFollower

from controllers.abstract_handler import AbstractHandler


################################################################################
# Volunteers page
class VolunteersPage(AbstractHandler):
  LIMIT = 12
  ################################################################################
  # GET
  def get(self, url_data):

    if url_data:
      if '/search' == url_data:
        params = Parameters.parameterize(self.request)
        self.search(params)
      else:
        self.show(url_data[1:])        
    else:
      self.list() 

  ################################################################################
  # SHOW
  def show(self, volunteer_id):
    try:
      account = self.auth(require_login=True)
    except:
      return
  
    volunteer = account.get_user()
    if volunteer and volunteer.key().id() == int(volunteer_id):
      self.redirect("/settings");
      return

    #TODO: if application instances are closed, do not allow people to view
    if not volunteer:
      self.redirect("/settings")
      return

    page_volunteer = Volunteer.get_by_id(int(volunteer_id))

    if not page_volunteer:
      self.error(404)
      return

    volunteerfollower = page_volunteer.account.followers.filter('account =', account).get()
                      
    volunteerfollowing = account.followers.filter('account =', page_volunteer.account).get()
                                            
    event_access = page_volunteer.event_access(account = account) 
                      
    future_events = page_volunteer.events_future()[:VolunteersPage.LIMIT]
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 
                        'volunteerfollower' : volunteerfollower,
                        'volunteerfollowing' : volunteerfollowing,
                        'page_volunteer': page_volunteer,
                        'volunteer' : volunteer,
                        'event_access': event_access,
                        'future_events': future_events
                        }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'view_other_volunteer.html')
    self.response.out.write(template.render(path, template_values))


  ################################################################################
  # LIST
  def list(self):
    return
  
  ################################################################################
  # SEARCH
  def search(self, params):
    try:
      account = self.auth(require_login=True)
    except:
      return
    
    (name, email, neighborhood, volunteers)  = self.do_search(params)
    template_values = { 
      'neighborhood' : neighborhood,
      'email' : email,
      'name' : name,
      'volunteers' : volunteers,
      'volunteer' : account.get_user(),
    }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'volunteers_search.html')
    self.response.out.write(template.render(path, template_values))

  def do_search(self, params):
      
    #todo: get volunteers from this application only
    application = get_application()
    volunteers_query = Volunteer.all().filter('applications =', application.key().id())
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
    
    if 'email' in params and params['email']:
      try:
        email = params['email'] 
        volunteers_query.filter('preferred_email =', email)
      except:
        pass

    volunteers = volunteers_query.fetch(limit = 100)

    return (name, email, neighborhood, volunteers)


################################################################################
# FollowVolunteer

from components.message_text import type2
from controllers._utils import send_message
from models.messages import MessageType

class FollowVolunteer(AbstractHandler):

    ################################################################################
    # POST
    def post(self, url_data):
        try:
            account = self.auth(require_login=True)
        except:
            return
        
        to_follow = Volunteer.get_by_id(int(url_data))
        
        if to_follow:
            volunteerfollower = to_follow.account.followers.filter('account =', account).get()

            if self.request.get('delete') and self.request.get('delete') == "true":
                if volunteerfollower:
                    volunteerfollower.delete()
            else:
                if not volunteerfollower:
                    volunteerfollower = VolunteerFollower(follows=to_follow.account, follower=account)
                    volunteerfollower.put()
                    params = self.get_message_params(adder = account, account = to_follow.account, volunteer = to_follow)
                    subject = type2.subject%params
                    body = type2.body%params
                    send_message( 
                        to = [to_follow.account], 
                        subject = subject, 
                        body = body, 
                        type = MessageType.all().filter('name =', 'added_to_team').get())   
        
        #self.redirect('/volunteers/' + url_data)
        self.redirect(self.request.referrer)
        
        return
    
    def get_message_params(self,adder, account, volunteer):
        params = {
            'adder_name': adder.name,
            'vol_name': account.name,
            'adder_url': '%s%s'%(self._get_base_url(), adder.get_user().url()),
            'vol_team_url': '%s%s'%(self._get_base_url(), volunteer.url()), 
            'reciprocation':''
        }
        
        reciprocal = adder.following.filter('account =', volunteer.account).get()
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
      account = self.auth(require_login=True)
    except:
      return
      
    params = Parameters.parameterize(self.request)
    
    if 'delete_avatar' in params and params['delete_avatar'] == 'true':
      self.delete(account)
    else:
      self.update(params, account)

    self.redirect('/settings')
  
  ################################################################################
  # DELETE
  def delete(self, account):
    user = account.get_user()
    user.avatar = None
    user.put()
    
  ################################################################################
  # UPDATE
  def update(self, params, account):
    if 'avatar' in params and params['avatar']:
      if len(params['avatar']) > 50 * 2**10:
        return
        
      content_type = imghdr.what(None, params['avatar'])
      if not content_type:
        return

      user = account.get_user()
      user.avatar_type = 'image/' + content_type
      user.avatar = params['avatar']
      user.put()

    