from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from controllers._auth import Authorize
from models.neighborhood import Neighborhood

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(webapp.RequestHandler):
  def get(self, url_data):    
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return
    
    template_values = {
        'volunteer': volunteer,
        'neighborhoods': sorted(Neighborhood.all(), lambda a,b:cmp(a.name,b.name))
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.html')
    self.response.out.write(template.render(path, template_values))
    return
    
class NeighborhoodDetailPage(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):
    if url_data:
      self.show(url_data)
    else:
      self.list() 

  ################################################################################
  # POST

  ################################################################################
  # SHOW
  def show(self, neighborhood_id):
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return

    neighborhood = Neighborhood.get_by_id(int(neighborhood_id))

    template_values = {
        'volunteer': volunteer,
        'neighborhood': neighborhood
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
    return
