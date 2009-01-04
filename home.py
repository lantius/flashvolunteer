import cgi
import wsgiref.handlers
import os
import logging


from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
  def get(self):
    template_values = { 
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

################################################################################
# models
################################################################################
class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.StringProperty()

class Event(db.Model):
  name = db.StringProperty()
  date = db.DateProperty()
  neighborhood = db.StringProperty()
  
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'volunteers')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'events')
  isowner = db.BooleanProperty(required = True)

################################################################################
# gae mojo
################################################################################
def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication(
                                    [('/', MainPage),
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()


