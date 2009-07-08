import os, string
import imghdr

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._auth import Authorize
from controllers._params import Parameters

from models.volunteer import *
from models.volunteerfollower import *

################################################################################
# Volunteers page
class VolunteersPage(webapp.RequestHandler):

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
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
      
    if volunteer and volunteer.key().id() == int(volunteer_id):
      self.redirect("/settings");
      return

    if not volunteer or not volunteer.session_id:
      self.redirect("/setting")
      return

    page_volunteer = Volunteer.get_by_id(int(volunteer_id))

    if not page_volunteer:
      self.error(404)
      self.response.out.write('404 page! boo!')

    volunteerfollower = VolunteerFollower.gql("WHERE volunteer = :volunteer AND follower = :follower" ,
                      volunteer=page_volunteer, follower=volunteer).get()
                      
    volunteerfollowing = VolunteerFollower.gql("WHERE volunteer = :volunteer AND follower = :follower" ,
                      volunteer=volunteer, follower=page_volunteer).get()
                                            
    event_access = page_volunteer.event_access(volunteer = volunteer) 
                      
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 
                        'volunteerfollower' : volunteerfollower,
                        'volunteerfollowing' : volunteerfollowing,
                        'page_volunteer': page_volunteer,
                        'volunteer' : volunteer,
                        'event_access': event_access,
                        'session_id' : volunteer.session_id
                        }
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
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    
    (name, email, neighborhood, volunteers)  = self.do_search(params)
    template_values = { 
      'neighborhood' : neighborhood,
      'email' : email,
      'name' : name,
      'volunteers' : volunteers,
      'volunteer' : volunteer,
      'session_id' : volunteer.session_id,
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'volunteers_search.html')
    self.response.out.write(template.render(path, template_values))

  def do_search(self, params):
    volunteers_query = Volunteer.all()
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

    volunteers = volunteers_query.fetch(limit = 25)

    return (name, email, neighborhood, volunteers)


################################################################################
# FollowVolunteer
class FollowVolunteer(webapp.RequestHandler):

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    to_follow = Volunteer.get_by_id(int(url_data))

    if to_follow:
      volunteerfollower = VolunteerFollower.gql("WHERE volunteer = :volunteer AND follower = :follower" ,
      volunteer=to_follow, follower=volunteer).get()
      if self.request.get('delete') and self.request.get('delete') == "true":
        if volunteerfollower:
          volunteerfollower.delete()
      else:
        if not volunteerfollower:
          volunteerfollower = VolunteerFollower(volunteer=to_follow, follower=volunteer)
          volunteerfollower.put()

    #self.redirect('/volunteers/' + url_data)
    self.redirect(self.request.referrer)

    return


################################################################################
# VolunteerAvatar
class VolunteerAvatar(webapp.RequestHandler):
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
      volunteer = Authorize.login(self, requireVolunteer=True)
    except:
      return
      
    params = Parameters.parameterize(self.request)
    
    if 'delete_avatar' in params and params['delete_avatar'] == 'true':
      self.delete(volunteer)
    else:
      self.update(params, volunteer)

    self.redirect('/settings')
  
  ################################################################################
  # DELETE
  def delete(self, volunteer):
    volunteer.avatar = None
    volunteer.put()
    
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    if 'avatar' in params and params['avatar']:
      if len(params['avatar']) > 50 * 2**10:
        return
        
      content_type = imghdr.what(None, params['avatar'])
      if not content_type:
        return

      volunteer.avatar_type = 'image/' + content_type
      volunteer.avatar = params['avatar']
      volunteer.put()

################################################################################
# VolunteerTeam
class VolunteerTeam(webapp.RequestHandler):

  def get(self, volunteer_id, page):
    if volunteer_id:
      self.show(volunteer_id, int(page))
    else:
      self.list() 

  def show(self, volunteer_id, page):
    LIMIT = 2
    
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
          
    page_volunteer = Volunteer.get_by_id(int(volunteer_id))

    if not page_volunteer:
      self.error(404)
      self.response.out.write('404 page! boo!')
    
    total = page_volunteer.volunteerfollowing.count()
    start = (page-1) * LIMIT + 1
    
    team = [vf.volunteer for vf in page_volunteer.volunteerfollowing.fetch(limit = LIMIT, offset=start - 1)]

    
    end = start + len(team) - 1
                                                
    if end == total:
        next_page = -1
    else: 
        next_page = page + 1
    
    if page == 1:
        prev_page = -1
    else:
        prev_page = page -1
        
    template_values = { 
                        'page_volunteer': page_volunteer,
                        'volunteer' : volunteer,
                        'team': team,
                        'session_id' : volunteer.session_id,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page
                        }
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'view_other_volunteer', 'team.html')
    self.response.out.write(template.render(path, template_values))

    