import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models.volunteer import *
from models.volunteerfollower import *

################################################################################
# Volunteers page
class VolunteersPage(webapp.RequestHandler):

  ################################################################################
  # GET
  def get(self, url_data):

    if url_data:
      self.show(url_data[1:])
    else:
      self.list() 

  ################################################################################
  # POST

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
                      
                      
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 
                        'volunteerfollower' : volunteerfollower,
                        'page_volunteer': page_volunteer,
                        'volunteer' : volunteer,
                        'session_id' : volunteer.session_id
                        }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'volunteer.html')
    self.response.out.write(template.render(path, template_values))


  ################################################################################
  # LIST
  def list(self):
    return
    

################################################################################
# FollowVolunteer
class FollowVolunteer(webapp.RequestHandler):

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='settings')
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

    self.redirect('/volunteers/' + url_data)
    return


################################################################################
# VolunteerAvatar
class VolunteerAvatar(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):
    volunteer = Volunteer.get_by_id(int(url_data))
    if volunteer.avatar:
      self.response.headers['Content-Type'] = "image/jpg"
      self.response.out.write(volunteer.avatar)
    else:
      self.error(404)