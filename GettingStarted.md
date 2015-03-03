Flash Volunteer is written in [Python](http://www.python.org). We are using [Google App Engine](http://code.google.com/appengine/docs/), which acts as both a Django-based web framework and cloud-based hosting platform.

This document outlines what you need to do to get up and running as a Flash Volunteer developer (or tester, though there's much more information than a tester needs here).

There's a lot of information in here. Don't be overwhelmed. You don't need to understand everything before you start trying things out.

  1. **Install the necessary software** Install Python, Google App Engine, and an IDE. See the [Installation Directions](http://code.google.com/p/flashvolunteer/wiki/Installation).
  1. **Download the Flash Volunteer code** Use Subversion to check out the Flashvolunteer code from code.google.com. Instructions are [here](http://code.google.com/p/flashvolunteer/wiki/SVNCheckout).
  1. **Getting cozy with the tools**
    * **Python**. If you are not familiar with Python, you might want to try the [Python tutorial](http://docs.python.org/tutorial/). I'll just say that Python is the best language ever :) You'll be a better human being after learning it.
    * **Google App Engine** If you've not worked with Appengine before, do the [Hello World tutorial](http://code.google.com/appengine/docs/python/gettingstarted/helloworld.html). Its also a good idea to [look through their documentation](http://code.google.com/appengine/docs/python/gettingstarted/) too.
  1. **Hacking**
    * A [description of the code structure](http://code.google.com/p/flashvolunteer/wiki/GuideToTheCode)
    * A [coding style guide](http://code.google.com/p/flashvolunteer/wiki/StyleGuide) (check out https://seattle.cs.washington.edu/wiki/CodingStyle)
    * The testing environment. Deploying your code. [Testing and deploying](TestingDeploying.md)



---



# Leftover documentation #

Not sure if this stuff is useful, but I left it in anyway...

## Stepthrough ##
  * request: html://flashvolunteer.appspot.com/events
> > show events page
  * app.yaml
```
      url: /.*
      script: controllers/route.py
```
  * app.yaml	- route request
  * controller/route.py	- further routes incoming requests
```
      def main():
        application = webapp.WSGIApplication(	
          ...
          ('/events(|/\d+|/new|/search)', EventsPage),
				...
				)
```
  * controller/event.py
```
       def get(self, url_data):    
          ...
          else:
            self.list()
```
  * controller/event.py
```
       def list(self):
         volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
         #fill in template in views/events/events.html
```
  * django template: ` views/events/events.html, extend views/_layout.html `
> > includes blocks ` _volunteer_upcoming.html, _volunteer_past.html, find_event_wide.html, _recommended_events.html `
    * ` views/_layout.html: ` places blocks, block content provided in views/events.html
    * ` _volunteer_upcoming.html: `
      * volunteer.events\_future() - future events from volunteer.events()
      * volunteer.events()	- list ` volunteer.eventvolunteers[n].event `
      * ` includes events/_upcoming_brief.html for each event `
> > > > event.name, event.get\_date, event.neighborhood.name etc.
      * where does volunteer.eventvolunteers come from?
```
         class EventVolunteer(db.Model):
         volunteer = db.ReferenceProperty(Volunteer, required = True, collection_name = eventvolunteers')
         #volunteer.eventvolunteers is query for all records in EventVolunteer that match this volunteer instance
```

## FAQ ##

  * where is data stored, and how can it be manipulated?

> > app engine storage, can access through
    * http://localhost:8080/_ah/admin/datastore
    * remote data api?
    * open source projects?
  * what data needs needs to be set up by hand, and how?
    * neighborhoods
    * create rights for events must have create\_rights to create event (shows up as tab)
  * what happens to ` EventVolunteer ` if volunteer is deleted?
  * what happens if models evolve, more variables, how are old instances updated