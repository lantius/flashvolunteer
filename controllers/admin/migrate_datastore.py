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
from models.eventinterestcategory import EventInterestCategory
from models.auth.account import Account

import os, logging

from google.appengine.ext import deferred


def clean_accounts():
    for v in Volunteer.all(): 
        acnts = Account.all().filter('user =', v.user).filter('name =', v.get_name()).fetch(10)
        for a in acnts:
            if not a.get_user():
                for auth in a.auth_methods:
                    auth.delete()
                a.delete()
            else:
                meths = a.auth_methods.fetch(20)
                if len(meths) > 1:
                    for auth in meths[1:]:
                        auth.delete()
                elif len(meths) == 0:
                    a.delete()
                    
    

def clean_null_users():
    vols = Volunteer.all().filter('user =', None).fetch(100)
    for v in vols:
        v.delete()

    
def migrate_accounts():
    from models.auth import Auth, Account
    for v in Volunteer.all():
        
        if not Account.all().filter('user =', v.user).filter('name =', v.get_name()).get():
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
                strategy = 'MyOpenID'
            else: 
                strategy = 'Google'

            try:
                account.put()
            except:
                raise
            
            
            auth = Auth(
                strategy = strategy,
                identifier = v.user.email(),
                account = account
            )            

        
            try:
                auth.put()
            except:
                account.delete()
                raise

            v.account = account

            try:    
                v.put()
            except:
                auth.delete()
                account.delete()
                raise


def migrate_vfs():
    from models.volunteerfollower import VolunteerFollower
    for vf in VolunteerFollower.all():
        changed = False
        if vf.volunteer:
            if vf.follows != vf.volunteer.account:
                vf.follows = vf.volunteer.account
                changed = True
                
            if isinstance(vf.follower, Volunteer):                    
                vf.follower = vf.follower.account
                changed = True
            
        mutual = vf.follows.following.filter('follows =', vf.follower).get()
        if vf.mutual != mutual is not None:
            vf.mutual = mutual is not None
            changed = True
        
        if changed:
            vf.put()
            
def migrate_messages_prefs():
    from models.messages import MessageReceipt, MessagePreference, Message
    for mp in MessagePreference.all():
        if mp.volunteer and not mp.account:
            mp.account = mp.volunteer.account
            mp.put()

def migrate_messages():          
    from models.messages import MessageReceipt, MessagePreference, Message

    for m in Message.all():
        if m.sent_by:
            try:
                m.sent_by = m.sent_by.account
                m.put()
            except:
                pass

def migrate_messages_receipt():
    from models.messages import MessageReceipt, MessagePreference, Message    
    for mr in MessageReceipt.all():
        try:
            mr.recipient = mr.recipient.account
            mr.put()
        except:
            pass

def migrate_event_photos():
    from models.eventphoto import EventPhoto
    for ep in EventPhoto.all():
        if ep.account != ep.volunteer.account:
            ep.account = ep.volunteer.account
            ep.put()

def migrate_events():            
    for e in Event.all():
        if not e.in_past:
            e.in_past = e.inpast()
            e.put()

def migrate_interests():
    from models.interest import Interest
    from models.volunteerinterestcategory import VolunteerInterestCategory
        
    for v in Volunteer.all():
        cnt = v.volunteerinterestcategories.count()
        if cnt > 0:
            a = v.account
            if cnt > a.user_interests.count():
                interests = dict([(i.interestcategory.key().id(), 1) for i in a.user_interests])
                
                for vic in v.volunteerinterestcategories:
                    ic = vic.interestcategory
                    if ic.key().id() not in interests:
                        i = Interest(account = a, interestcategory = ic)
                        i.put()
        
def migrate_event_interests():        
    for eic in EventInterestCategory.all():
        eic.event_is_upcoming = not eic.event.inpast()
        eic.put()


def migrate_event_vols():
    from models.eventvolunteer import EventVolunteer
    for ev in EventVolunteer.all():
        ev.event_is_upcoming = not ev.event.inpast()
        ev.event_is_hidden = ev.event.hidden
        ev.event_date = ev.event.date
        ev.application = ev.event.application

        if ev.volunteer and not ev.account:
            ev.account = ev.volunteer.account
        elif ev.account and not ev.volunteer:
            ev.volunteer = ev.account.get_user()
        ev.put()

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
#        deferred.defer(clean_null_users)
#        deferred.defer(clean_accounts)
#        deferred.defer(migrate_accounts)

        #deferred.defer(migrate_vfs)
        deferred.defer(migrate_events)
        #deferred.defer(migrate_event_vols)
        #deferred.defer(migrate_messages)
        #deferred.defer(migrate_messages_receipt)
        #deferred.defer(migrate_messages_prefs)
        #deferred.defer(migrate_interests)
        deferred.defer(migrate_event_interests)

        
        


        return 'successful'
        
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