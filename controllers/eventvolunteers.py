import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import *
from models.event import *
from models.eventvolunteer import *

from controllers._auth import Authorize
from controllers._utils import send_mail

################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(webapp.RequestHandler):

  ################################################################################
  # POST
    def post(self, url_data):
        try:
          volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
        except:
          return
        
        event = Event.get_by_id(int(url_data))
        
        if event:
          eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = false AND event = :event" ,
                              volunteer=volunteer, event=event).get()
          if self.request.get('delete') and self.request.get('delete') == "true":
            if eventvolunteer:
              eventvolunteer.delete()
              (sender, to, subject, body) = self.get_message_text(event = event, 
                                                                  volunteer = volunteer, 
                                                                  sign_up = False)
              try: 
                  send_mail(sender = sender, to = to, subject = subject, body = body)
              except:
                  pass
          else:
            if not eventvolunteer:
              eventvolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=False)
              eventvolunteer.put()
              (sender, to, subject, body) = self.get_message_text(event = event, 
                                                                  volunteer = volunteer,
                                                                  sign_up = True)
        
              try: 
                  send_mail(sender = sender, to = to, subject = subject, body = body)
              except:
                  pass
            
        self.redirect('/events/' + url_data)
        return

    def get_message_text(self, event, volunteer, sign_up = True):
        #TODO email multiple owners
        owner = EventVolunteer.gql("WHERE isowner = true AND event = :event" ,
                          event=event).get()
                          
        owner = owner.volunteer
        sender="Flash Volunteer <info@flashvolunteer.org>"
        to = '%(owner_name)s <%(owner_email)s>'
        
        if sign_up:
            subject = 'A volunteer has signed up for %s'%event.name
            body="""
Hi %(owner_name)s,

%(vol_name)s has signed up for \"%(event_name)s\". You now have %(vol_count)s volunteer(s) signed up. 
"""
    
        else:
            subject = 'Someone unvolunteered for %(event_name)s'
            body="""
Hi %(owner_name)s,

Someone decided they could not help out at \"%(event_name)s\". You now have %(vol_count)s volunteer(s) signed up. 
"""
            
        body += """
To manage your event, visit %(event_url)s. 
    
Please let us know if you have any questions or if you would prefer not to get emails like this.
    
The Flash Volunteer Team
"""
                    
        #TODO : event url needs to account for which FV application this is
        params = {
            'event_name': event.name.strip(),
            'owner_name': owner.get_name().strip(),
            'owner_email': owner.get_email().strip(),
            'event_url': 'http://%s%s'%(os.environ['HTTP_HOST'], event.url()),
            'vol_count': EventVolunteer.gql("WHERE isowner = false AND event = :event" ,event=event).count(),
            'vol_name': volunteer.get_name()
        }
        body = body%params
        subject = subject%params
        to = to%params
        
        return sender, to, subject, body