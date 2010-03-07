from google.appengine.ext import db
from models.volunteer import Volunteer

################################################################################
# Organization
class Organization(db.Model):
    
    name = db.StringProperty()
    email = db.StringProperty(default=None)
    admin = db.ReferenceProperty(Volunteer, collection_name = 'organization_admins')
        
