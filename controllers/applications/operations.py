from models.application import Application
from models.applicationdomain import ApplicationDomain

from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.messages.message_type import MessageType
from models.messages.message_propagation_type import MessagePropagationType

from controllers._utils import get_server, get_application

import os

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
    message_props = (
        ('mailbox', 'Flash Mailbox'),
        ('email', 'Email')
    )

    mps = {}
    for mp, prompt in message_props: 
        if MessagePropagationType.all().filter('name =', mp).count() > 0: 
            mpt = MessagePropagationType.all().filter('name =', mp).get()       
        else:
            mpt = MessagePropagationType(name = mp, prompt = prompt)
            mpt.put()
        mps[mp] = mpt
        
    message_types = (
        (1, 'event_coord', 'When someone signs up for an event you coordinate', ['mailbox','email']),
        (2, 'added_to_team', 'When someone adds you to their team', ['mailbox','email']),
        (3, 'welcome', 'When you create an account', ['mailbox'])
    )

    for order, name, prompt, mpts in message_types:
        defaults = [mps[mp].key().id() for mp in mpts]
        if MessageType.all().filter('name =', name).count() > 0:         
            mt = MessageType.all().filter('name =', name).get()
            if mt.prompt != prompt or defaults != mt.default_propagation or order != mt.order:
                mt.prompt = prompt
                mt.order = order
                mt.default_propagation = defaults
                mt.put()
        else: 
            mt = MessageType(
                name = name,
                order = order,
                prompt = prompt,
                default_propagation = defaults,
            )
            mt.put()

def add_applications(applications):
        
    server = get_server()
    if server == 0:
        from gui_integration_tests.test_settings import host
        domains = [host]
    elif server == 1:
        domains = ['flashvolunteer-dev.appspot.com', 'development.flashvolunteer.org']
    else:
        domains = ['flashvolunteer.org']

    for application_def in applications: 
        if Application().all().filter('name =', application_def.get_name()).count() == 0: 
            a = Application(name = application_def.get_name())
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
    
    for hood in application_def.get_neighborhoods():
        if Neighborhood.all().filter('name =', hood).count() > 0: 
            continue
        n = Neighborhood(name = hood, application = application)
        n.put()