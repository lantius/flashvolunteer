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

    candidates = list(category.volunteers_interested())
    template_values = {
        'volunteer': volunteer,
        'category': category,
        'volunteers_interested': random.sample(candidates, min(len(candidates), LIMIT))
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category.html')
    self.response.out.write(template.render(path, template_values))
    return


