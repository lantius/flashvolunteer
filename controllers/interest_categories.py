from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

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
  def show(self, neighborhood_id):
    try:
      volunteer = Authorize.login(self, requireVolunteer=False, redirectTo='/settings')
    except:
      return

    category = InterestCategory.get_by_id(int(neighborhood_id))

    template_values = {
        'volunteer': volunteer,
        'category': category
      }

    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'categories', 'category.html')
    self.response.out.write(template.render(path, template_values))
    return
