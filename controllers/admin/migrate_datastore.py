from components.sessions import Session
from controllers._utils import get_server, get_application
from components.applications.operations import add_applications, add_messaging, synchronize_apps
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import webapp
from models.application import Application
from models.applicationdomain import ApplicationDomain
from models.event import Event
from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer

import os, logging

class MigrateDatastore(AbstractHandler):

    def get(self):
        
        ## do migration here
        synchronize_apps()
#        from models.messages import MessageReceipt
#        from components.time_zones import utc, Pacific
#        
#        for mr in MessageReceipt.all():
#            mr.emailed = True
#            logging.info('converting time from: \n%s to\n'%mr.timestamp)
#            mr.timestamp = mr.timestamp.replace(tzinfo=Pacific).astimezone(utc)
#            logging.info(mr.timestamp)
#            mr.put()
#        
#        from models.messages import Message
#        for m in Message.all():
#            m.trigger = m.trigger.replace(tzinfo=Pacific).astimezone(utc)
#            m.put()

        from models.auth import Auth, Account
        for v in Volunteer.all():
            if not v.account:
                account = Account(
                    user = v.user,
                    preferred_email = v.get_email(),
                    active_applications = v.applications,
                    name = v.get_name()
                )
                
                if v.user.email().find('@yahoo') > -1:
                    strategy = 'Yahoo!'
                elif v.user.email().find('@Facebook') > -1:
                    strategy = 'Facebook'
                elif v.user.email().find('/') > -1:
                    strategy = 'OpenID'
                else: 
                    strategy = 'Google'
                    
    
                account.put()
    
                auth = Auth(
                    strategy = strategy,
                    identifier = v.user.email(),
                    account = account
                )
                auth.put()
                
                v.account = account
                v.put()
        
        
        from models.messages import MessageReceipt, MessagePreference, Message
        for mp in MessagePreference.all():
            if mp.volunteer:
                mp.account = mp.volunteer.account
                mp.put()
        for m in Message.all():
            if m.sent_by:
                m.sender = m.sent_by.account
                m.put()
        for mr in MessageReceipt.all():
            mr.recipient2 = mr.recipient.account
            mr.put()
        
        from models.eventphoto import EventPhoto
        for ep in EventPhoto.all():
            ep.account = ep.volunteer.account
            ep.put()
            
        from models.eventvolunteer import EventVolunteer
        for ev in EventVolunteer.all():
            if ev.volunteer:
                ev.account = ev.volunteer.account
                ev.put()
            
        from models.volunteerfollower import VolunteerFollower
        for vf in VolunteerFollower.all():
            if vf.volunteer:
                vf.follows = vf.volunteer.account
                vf.follower2 = vf.follower.follower2
                vf.put()
            
        from models.interest import Interest
        from models.volunteerinterestcategory import VolunteerInterestCategory
        for vic in VolunteerInterestCategory.all():
            if vic.volunteer:
                i = Interest(account = vic.volunteer.account, interestcategory = vic.interestcategory)
                i.put()
            
        return
    
##########################################################################
## Various migration methods that may or may not be useful in the future.
##########################################################################
        
    def __set_default_application_data(self):
        logging.info('MIGRATE: add application data')
        seattle = Application.all().filter('name =', "seattle").get()
        for v in Volunteer.all():
            
            if not v.applications:
                v.add_application(seattle)
                logging.info('MIGRATE: added seattle to volunteer "%s"'%v.name)

        for e in Event.all():
            try:
                if e.application is None:
                    e.application = seattle
                    e.put()
                    logging.info('MIGRATE: added seattle to event "%s"'%e.name)
            except:
                e.application = seattle
                e.put()
                logging.info('MIGRATE: added seattle to event "%s"'%e.name)

        for n in Neighborhood.all():
            try:
                if not n.application:
                    n.application = seattle
                    n.put()
                    logging.info('MIGRATE: added seattle to neighborhood "%s"'%e.name)
            except:
                n.application = seattle
                n.put()
                logging.info('MIGRATE: added seattle to neighborhood "%s"'%e.name)
                
    def __migrate_neighborhoods(self):
        #neighborhoods to add
        new_hoods = []
        
        hoods = {}
        for n in Neighborhood.all():
            hoods[n.name] = n
            
                      
        for n in new_hoods:
            if not n in hoods:
                hood = Neighborhood(name = n)
                hood.put()
                hoods[n] = hood
                
        #neighborhood transformations; 
        #### From : To
        n_map =  {
                 #'South Lake Union': 'Lake Union',
                 }     
            
        for v in Volunteer.all():
            if v.work_neighborhood and v.work_neighborhood.name in n_map:
                v.work_neighborhood = hoods[n_map[v.work_neighborhood.name]]
                v.put()
            if v.home_neighborhood and v.home_neighborhood.name in n_map:
                v.home_neighborhood = hoods[n_map[v.home_neighborhood.name]]
                v.put()
                
        for e in Event.all():
            if e.neighborhood and e.neighborhood.name in n_map:
                e.neighborhood = hoods[n_map[e.neighborhood.name]]
                e.put()
                
        #neighborhoods to delete
        hoods_to_remove = []      
        for n in hoods_to_remove:
            if n in hoods:
                hoods[n].delete()  
            
    def __clear_stale_events(self):
        for ev in EventVolunteer.all():
            try:
                event = ev.event
            except:
                ev.delete()
                
        for ec in EventInterestCategory.all():
            try:
                event = ec.event
            except:
                ec.delete()