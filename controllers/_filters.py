from google.appengine.ext import webapp
from django import template

register = webapp.template.create_template_register()

def team_status(parser, token):
    try:
        tag_name, volunteer, volunteer2 = token.split_contents()
    except ValueError:
        return None
    return RelationshipStatusNode(volunteer = volunteer, volunteer2 = volunteer2)

class RelationshipStatusNode(template.Node):
    def __init__(self, volunteer, volunteer2):
        self.volunteer = volunteer
        self.volunteer2 = volunteer2 
        
    def render(self, context):
        volunteer = template.resolve_variable(self.volunteer,context)
        try:
            volunteer2 = template.resolve_variable(self.volunteer2,context)
        except:
            context['is_teammate'] = False
            return ''
        if volunteer:
            context['is_teammate'] = volunteer.following.filter('followed =', volunteer2).get() is not None
        return ''

register.tag(team_status)

#############################################################

def message_type_pref(parser, token):
    try:
        tag_name, volunteer, message_type, propagation_type = token.split_contents()
    except ValueError:
        return None
    return MessageTypePrefNode(volunteer = volunteer, 
                               message_type = message_type, 
                               propagation_type = propagation_type)

class MessageTypePrefNode(template.Node):
    def __init__(self, volunteer, message_type, propagation_type):
        self.volunteer = volunteer
        self.message_type = message_type
        self.propagation_type = propagation_type 
        
    def render(self, context):
        volunteer = template.resolve_variable(self.volunteer,context)
        propagation_type = template.resolve_variable(self.propagation_type,context)
        message_type = template.resolve_variable(self.message_type,context)
        
        if volunteer:
            mp = volunteer.message_preferences.filter('type =', message_type).get()
            if not mp: 
                prop = message_type.default_propagation
            else:
                prop = mp.propagation
            
            context['mt_checked'] = propagation_type.key().id() in prop
        return ''

register.tag(message_type_pref)
 
    
