import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models import Volunteer, VolunteerFollower


################################################################################
# Volunteers page
################################################################################
class VolunteersPage(webapp.RequestHandler):

  ################################################################################
  # GET
  ################################################################################
  def get(self, url_data):
    if url_data:
      self.show(url_data[1:])
    else:
      self.list() 

  ################################################################################
  # SHOW
  ################################################################################
  def show(self, volunteer_id):
    (user, volunteer) = Authorize.login(self)

    if volunteer and volunteer.key().id() == int(volunteer_id):
      self.redirect("/settings");
      return

    logout_url =''

    if user:
      logout_url = users.create_logout_url(self.request.uri)

    page_volunteer = Volunteer.get_by_id(int(volunteer_id))
    volunteerfollower = VolunteerFollower.gql("WHERE volunteer = :volunteer AND follower = :follower" ,
                        volunteer=page_volunteer, follower=volunteer).get()
                        
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 
                        'volunteerfollower' : volunteerfollower,
                        'volunteer': page_volunteer,
                        'session_id' : volunteer.session_id,
                        'logout_url': logout_url}
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteer.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # LIST
  ################################################################################
  def list(self):
    return
    

################################################################################
# FollowVolunteer
################################################################################
class FollowVolunteer(webapp.RequestHandler):

  ################################################################################
  # POST
  ################################################################################
  def post(self, url_data):
     (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='/settings')

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

     self.redirect('/volunteers/' + url_data)
     return
  