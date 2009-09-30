import os, string
import imghdr

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._auth import Authorize
from controllers._params import Parameters
from controllers._utils import get_application

from models.organization import Organization
from models.organizationfollower import OrganizationFollower

################################################################################
# Organizations page
class OrganizationsPage(webapp.RequestHandler):
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
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    if volunteer and volunteer.key().id() == int(volunteer_id):
      self.redirect("/settings")
      return

    if not volunteer or not volunteer.session_id:
      self.redirect("/setting")
      return

    page_organization = Organization.get_by_id(int(organization_id))

    if not page_volunteer:
      self.error(404)
      return

    organizationfollower = OrganizationFollower.gql("WHERE organization = :organization AND follower = :follower" ,
                      organization=page_organization, follower=volunteer).get()

    event_access = page_volunteer.event_access(volunteer = volunteer) 

    future_events = page_volunteer.events_future()[:VolunteersPage.LIMIT]
    template_values = { 'eventvolunteer': page_volunteer.eventvolunteers, 
                        'volunteerfollower' : volunteerfollower,
                        'volunteerfollowing' : volunteerfollowing,
                        'page_volunteer': page_volunteer,
                        'volunteer' : volunteer,
                        'event_access': event_access,
                        'future_events': future_events
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
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'volunteers_search.html')
    self.response.out.write(template.render(path, template_values))

  def do_search(self, params):
    application = get_application()
    volunteers_query = Organization.all().filter('applications =', application)
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
class FollowOrganization(webapp.RequestHandler):

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    to_follow = Organization.get_by_id(int(url_data))

    if to_follow:
      organizationfollower = OrganizationFollower.gql("WHERE organization = :organization AND follower = :follower" ,
      organization=to_follow, follower=volunteer).get()
      if self.request.get('delete') and self.request.get('delete') == "true":
        if organizationfollower:
          organizationfollower.delete()
      else:
        if not organizationfollower:
          orgaizationfollower = OrganizationFollower(organization=to_follow, follower=volunteer)
          orgaizationfollower.put()

    #self.redirect('/volunteers/' + url_data)
    self.redirect(self.request.referrer)

    return


################################################################################
# VolunteerAvatar
class OrganizationLogo(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):
    organization = Organization.get_by_id(int(url_data))
    if organization.logo:
      self.response.headers['Content-Type'] = str(organization.logo_type)
      self.response.out.write(organization.avatar)
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
    
    if 'delete_logo' in params and params['delete_logo'] == 'true':
      self.delete(organization)
    else:
      self.update(params, organization)

    self.redirect('/settings')
  
  ################################################################################
  # DELETE
  def delete(self, organization):
    organization.logo = None
    organization.put()
    
  ################################################################################
  # UPDATE
  def update(self, params, organization):
    if 'logo' in params and params['logo']:
      if len(params['logo']) > 50 * 2**10:
        return
        
      content_type = imghdr.what(None, params['logo'])
      if not content_type:
        return

      organization.logo_type = 'image/' + content_type
      organization.logo = params['logo']
      organization.put()

    