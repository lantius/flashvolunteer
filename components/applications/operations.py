from models.application import Application
from models.applicationdomain import ApplicationDomain

from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.messages.message_type import MessageType
from models.messages.message_propagation_type import MessagePropagationType

from components.applications.defs import regions
from google.appengine.ext import db

import os


def synchronize_apps(server):
    add_applications(server = server, applications=regions)
    add_categories()
    add_messaging()


def get_all_applications():
    self.tables_to_map = [f[:-3] for f in os.listdir(path) if fnmatch(f,'*.py') and f!='__init__.py']

def add_categories():
    categories = ("Animals","Arts & Culture","Children & Youth", "Education & Literacy", 
                  "Environment", "Gay, Lesbian, Bi, & Transgender", "Homeless & Housing",
                  "Hunger", "Justice & Legal", "Senior Citizens")
    for category_name in categories:
        if InterestCategory.all().filter('name =', category_name).count() > 0: 
            continue
        c = InterestCategory(name = category_name)
        c.put() 
      
def add_messaging(): 
    message_props = [
        ('email', 'Email')
    ]

    mps = {}
    for mp, prompt in message_props: 
        if MessagePropagationType.all().filter('name =', mp).count() > 0: 
            mpt = MessagePropagationType.all().filter('name =', mp).get()   
            if mpt.prompt != prompt:
                mpt.prompt = prompt
                mpt.put()    
        else:
            mpt = MessagePropagationType(name = mp, prompt = prompt)
            mpt.put()
        mps[mp] = mpt
        
    message_types = (
        (-1, 'site_wide', 'Flash Volunteer news updates (no more than once per week)', ['email'], True),

        (0, 'rec_event', 'Digest of upcoming, recommended events (weekly)', [], True),
        (1, 'person_to_person', 'If someone sends me a personal message', ['email'], True),

        (2, 'rsvp_vol', 'Reminder about an event I am volunteering at (24 hours notice)', ['email'], True),
        (3, 'rsvp_host', 'Reminder about an event I am coordinating (24 hours notice)', ['email'], True),
        
        (4, 'event_coord', 'If someone signs up for an event I\'m coordinating', ['email'], True),

        (5, 'post_vol', 'Reminder to give feedback on an event I attended', ['email'], True),
        (6, 'post_host', 'Reminder to fill out volunteer attendance for an event I coordinated', ['email'], True),

        (7, 'added_to_team', 'If someone adds me to their Flash team', ['email'], True),
        (8, 'welcome', 'When you create an account', [], False),

        #### Event_forum and neighborhood forum are the notifications that event_forum_main_message or neighborhood_main_message
        # was send. So individuals never receive an event of the latter two.
        (9, 'event_forum', 'When a message is posted for an event to which you are signed up', ['email'], True),
        (10, 'neighborhood_forum', 'When a message is posted to a neighborhood in which you are interested', [], True),

        (11, 'event_forum_main_message', '', [], False),
        (12, 'neighborhood_forum_main_message', '', [], False),
        ###########################################
    )

    for order, name, prompt, mpts, in_settings in message_types:
        defaults = [mps[mp].key().id() for mp in mpts]
        if MessageType.all().filter('name =', name).count() > 0:         
            mt = MessageType.all().filter('name =', name).get()
            if mt.prompt != prompt or defaults != mt.default_propagation or order != mt.order:
                mt.prompt = prompt
                mt.order = order
                mt.default_propagation = defaults
                mt.in_settings = in_settings
                mt.put()
        else: 
            mt = MessageType(
                name = name,
                order = order,
                prompt = prompt,
                default_propagation = defaults,
                in_settings = in_settings
            )
            mt.put()

def add_applications(server, applications):
        
    if server == 0:
        from gui_integration_tests.test_settings import host
        domains = [host]
    elif server == 1:
        domains = ['development.flashvolunteer.org', 'flashvolunteer-dev.appspot.com']
    else:
        domains = ['flashvolunteer.org']

    for application_def in applications: 
        if Application().all().filter('name =', application_def.get_name()).count() == 0: 
            a = Application(name = application_def.get_name(), 
                            ne_coord = application_def.ne_coord, 
                            sw_coord = application_def.sw_coord)
            a.put()
        else:
            a = Application().all().filter('name =', application_def.get_name()).get()
            if a.ne_coord != application_def.ne_coord:
                a.ne_coord = application_def.ne_coord                
                a.put()
            if a.sw_coord != application_def.sw_coord:
                a.sw_coord = application_def.sw_coord                
                a.put()
                
        add_application_subdomains(application_def = application_def,
                                   domains = domains)
        add_application_neighborhoods(application_def = application_def)

def add_application_subdomains(application_def, domains):
    ## INVARIANT: assumes that the Application has already been added
    
    application = Application().all().filter('name =', application_def.get_name()).get()
    if not application: raise
    
    fully_qual_domains = []
    for d in domains:
        for sd in application_def.get_subdomains():
            if sd == '':
                fully_qual_domains.append(d)
            else: 
                fully_qual_domains.append('%s.%s'%(sd,d))
    
    for fq in fully_qual_domains:
        if ApplicationDomain.all().filter('domain =', fq).count() > 0: 
            continue
        d = ApplicationDomain(domain = fq, application = application)
        d.put()
         
def add_application_neighborhoods(application_def):
    ## INVARIANT: assumes that the Application has already been added

    application = Application().all().filter('name =', application_def.get_name()).get()
    if not application: raise
    
    for hood, centroid_lat, centroid_lon in application_def.get_neighborhoods():
        if centroid_lat != None:
            centroid = db.GeoPt(lat = centroid_lat, lon = centroid_lon)
        else:
            centroid = None
        if Neighborhood.all().filter('name =', hood).count() > 0: 
            n = Neighborhood.all().filter('name =', hood).get()
            
            if n.centroid != centroid:
                n.centroid = centroid
                n.put()            
        else:
            n = Neighborhood(name = hood, application = application, centroid = centroid)
            n.put()