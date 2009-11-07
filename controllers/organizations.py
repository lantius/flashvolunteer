import os, string
import imghdr

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._params import Parameters
from controllers._utils import get_application

from models.organization import Organization
from models.organizationfollower import OrganizationFollower

from controllers.abstract_handler import AbstractHandler

################################################################################
# Organizations page
class OrganizationsPage(AbstractHandler):
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
  def show(self, organization_id):
    try:
      account = self.auth(require_login=True)
    except:
      return

    user = account.get_user()
    if user and uer.key().id() == int(organization_id):
      self.redirect("/settings")
      return
    
    session = Session()
    if not user or not session.sid:
      self.redirect("/setting")
      return

    page_organization = Organization.get_by_id(int(organization_id))

    if not page_organization:
      self.error(404)
      return

    organizationfollower = page_organization.account.followers.filter('account =', account).get()
    event_access = page_organization.event_access(account=account)
    
    future_events = page_organization.events_future()[:VolunteersPage.LIMIT]
    
    template_values = { 'eventvolunteer': page_organization.eventvolunteers, 
                        'volunteerfollower' : organizationfollower,
                        'page_volunteer': page_organization,
                        'volunteer' : user,
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
      'volunteer' : volunteer,
    }
    self._add_base_template_values(vals = template_values)
    
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
class FollowOrganization(AbstractHandler):

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      account = self.auth(require_login=True)
    except:
      return

    to_follow = Organization.get_by_id(int(url_data))

    if to_follow:
      organizationfollower = to_follow.account.followers.filter('account =', account).get()
      
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
class OrganizationAvatar(AbstractHandler):
  ################################################################################
  # GET
  def get(self, url_data):
    organization = Organization.get_by_id(int(url_data))
    if organization.avatar:
      self.response.headers['Content-Type'] = str(organization.avatar_type)
      self.response.out.write(organization.avatar)
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

    