from models.application import Application
from models.applicationdomain import ApplicationDomain
from models.event import Event
from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
    
from controllers._utils import get_server, get_application

import os

def get_all_applications():
    self.tables_to_map = [f[:-3] for f in os.listdir(path) if fnmatch(f,'*.py') and f!='__init__.py']

def add_categories():
    categories = ("Animals","Arts & Culture","Children & Youth", "Education & Literacy", 
                  "Environment", "Gay, Lesbian, Bi, & Transgender", "Homeless & Housing",
                  "Hunger", "Justice & Legal", "Senior Citizens")
    for category_name in categories:
      c = InterestCategory(name = category_name)
      c.put()  

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