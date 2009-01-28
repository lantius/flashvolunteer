import logging
from google.appengine.ext import webapp, db
import cgi
import wsgiref.handlers

from controllers.events import *
from models import *

class TestPage(webapp.RequestHandler):
  def get(self):
    message =""
    
    message += self.runUnitTests()

    self.response.out.write(message)
    
  def runUnitTests(self):
    message = ""
    
    message += self.runCreateEventTest()
    #TODO: More TESTS here

    return message
  
  def runCreateEventTest(self):
    message = ""
    w = webapp.RequestHandler()
    # what i would love is this
    #w.request.get('name') = 'failgate party'
    
    
    e = EventsPage()
    params = { 'name' : 'failgate party',
               'neighborhood' : 1 }
    volunteer = Volunteer()
    volunteer.put()

    ekey = e.create(params, volunteer)
    message += "Created " + str(ekey) + "\n"
    e.delete({'id' : ekey }, volunteer)
    message += "Deleted " + str(ekey) + "\n"
    return message

#class testrequest << webapp.requestHandler:


def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication(
                                    [('/test', TestPage),
                                    ],
                                    debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()

