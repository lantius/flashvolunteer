from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._auth import Authorize
from controllers._params import Parameters
from models.interestcategory import InterestCategory

################################################################################
# Neighborhoods page
################################################################################
class CategoryPage(webapp.RequestHandler):
  def get(self, url_data):
    
    if url_data:
      self.show(url_data)
    else:
      params = Parameters.parameterize(self.request)
      categories = InterestCategory.all().order('name').fetch(limit=500)
      template_values = {
          'categories': categories
      }
      is_json = self.is_json(params)
      if is_json:
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category.json')
        render_out = template.render(path, template_values)
        if (('jsoncallback' in params)):
          render_out = params['jsoncallback'] + '(' + render_out + ');'
          
        self.response.out.write(render_out)

  def is_json(self, params):
    if ((self.request.headers["Accept"] == "application/json") or 
         ('format' in params and params['format'] == 'json')):
       return True
    else:
       return False

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
    if not category:
      self.error(404)
      return
      
    candidates = list(category.volunteers_interested())

    past_events = list(category.past_events())        
    upcoming_events = list(category.upcoming_events())        
    
    template_values = {
        'volunteer': volunteer,
        'category': category,
        'volunteers_interested': random.sample(candidates, min(len(candidates), LIMIT)),
        'past_events': random.sample(past_events, min(len(past_events),LIMIT)),
        'upcoming_events':random.sample(upcoming_events, min(len(upcoming_events),LIMIT)),
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category.html')
    self.response.out.write(template.render(path, template_values))
    return


