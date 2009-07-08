from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

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
    LIMIT = 10
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return

    neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
    
    
    template_values = {
        'volunteer': volunteer,
        'neighborhood': neighborhood,
        'volunteers_living_here': random.sample(list(neighborhood.volunteers_living_here()), LIMIT), 
        'volunteers_working_here': random.sample(list(neighborhood.volunteers_working_here()), LIMIT), 
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
    return


################################################################################
# Pagination

def get_page_template(self, neighborhood_id, page):
    LIMIT = 10

    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
          
    neighborhood = Neighborhood.get_by_id(int(neighborhood_id))

    if not neighborhood:
      self.error(404)
      self.response.out.write('404 page! boo!')
    
    total = neighborhood.work_neighborhood.count()
    start = (page-1) * LIMIT + 1
    
    team = [v for v in neighborhood.work_neighborhood.fetch(limit = LIMIT, offset=start - 1)]

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
                        'neighborhood': neighborhood,
                        'volunteer' : volunteer,
                        'team': team,
                        'session_id' : volunteer.session_id,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page
                        }
    return template_values


class NeighborhoodVolunteerWorkPage(webapp.RequestHandler):

  def get(self, neighborhood_id, page):
    if neighborhood_id:
      self.show(neighborhood_id, int(page))
    else:
      self.list() 

  def show(self, neighborhood_id, page):
    
    template_values = get_page_template(self = self, neighborhood_id = neighborhood_id, page = page)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood_volunteer_work_page.html')
    self.response.out.write(template.render(path, template_values))


class NeighborhoodVolunteerHomePage(webapp.RequestHandler):

  def get(self, neighborhood_id, page):
    if neighborhood_id:
      self.show(neighborhood_id, int(page))
    else:
      self.list() 

  def show(self, neighborhood_id, page):
    template_values = get_page_template(self = self, neighborhood_id = neighborhood_id, page = page)
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood_volunteer_home_page.html')
    self.response.out.write(template.render(path, template_values))
