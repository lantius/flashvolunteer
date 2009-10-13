from google.appengine.ext import webapp
from django import template
from models.messages import MessagePreference

register = webapp.template.create_template_register()

def team_status(parser, token):
    try:
        tag_name, volunteer, volunteer_in_list = token.split_contents()
    except ValueError:
        return None
    return RelationshipStatusNode(volunteer = volunteer, volunteer_in_list = volunteer_in_list)

class RelationshipStatusNode(template.Node):
    def __init__(self, volunteer, volunteer_in_list):
        self.volunteer = volunteer
        self.volunteer_in_list = volunteer_in_list 
        
    def render(self, context):
        volunteer = template.resolve_variable(self.volunteer,context)
        volunteer_in_list = template.resolve_variable(self.volunteer_in_list,context)
        
        if volunteer:
          context['is_teammate'] = volunteer_in_list.key().id() in volunteer.teammates_ids()
        return ''

register.tag(team_status)

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
            mp = MessagePreference.all().filter('type =', message_type).get()
            if not mp: 
                prop = message_type.default_propagation
            else:
                prop = mp.propagation
            
            context['mt_checked'] = propagation_type.key().id() in prop
        return ''

register.tag(message_type_pref)