from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._auth import Authorize
from models.interestcategory import InterestCategory

################################################################################
# Neighborhoods page
################################################################################
class CategoryPage(webapp.RequestHandler):
  def get(self, url_data):
    if url_data:
      self.show(url_data)
    else:
      self.list() 

  ################################################################################
  # POST

  ################################################################################
  # SHOW
  def show(self, category_id):
    LIMIT = 12
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return

    category = InterestCategory.get_by_id(int(category_id))

    template_values = {
        'volunteer': volunteer,
        'category': category,
        'volunteers_interested': random.sample(list(category.volunteers_interested()), LIMIT)
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category.html')
    self.response.out.write(template.render(path, template_values))
    return

################################################################################
# Pagination


class CategoryVolunteerPage(webapp.RequestHandler):

  def get(self, category_id, page):
    if category_id:
      self.show(category_id, int(page))
    else:
      self.list() 

  def show(self, category_id, page):
    
    LIMIT = 12

    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
          
    category = InterestCategory.get_by_id(int(category_id))

    if not category:
      self.error(404)
      self.response.out.write('404 page! boo!')
    
    total = category.volunteerinterestcategories.count()
    start = (page-1) * LIMIT + 1
    
    team = [v.volunteer for v in category.volunteerinterestcategories.fetch(limit = LIMIT, offset=start - 1)]

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
                        'category': category,
                        'volunteer' : volunteer,
                        'team': team,
                        'session_id' : volunteer.session_id,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page
                        }    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category_detail', 'category_volunteer_page.html')
    self.response.out.write(template.render(path, template_values))
