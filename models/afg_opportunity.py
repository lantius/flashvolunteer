from google.appengine.ext import db

################################################################################
# AbstractUser
class AFGOpportunity(db.Model):

    #the ID as returned by AfG
    afg_id = db.StringProperty()
    
    #set to True or False when someone/something determines if the opportunity should be published on FV
    status = db.BooleanProperty(default=None)

    #metric for evaluating how suitable this opportunity is
    score = db.IntegerProperty(default=-1)
    
    #the start/end date of the opportunity as given by AfG
    startdate = db.DateTimeProperty(auto_now_add=False)
    enddate = db.DateTimeProperty(auto_now_add=False)
    
    title = db.StringProperty()
    provider = db.StringProperty()
    description = db.TextProperty()
    contact_email = db.StringProperty(default = None)
    skills = db.TextProperty()
    url = db.StringProperty()
    location = db.StringProperty()
    
    date_added = db.DateTimeProperty(auto_now_add=True)

