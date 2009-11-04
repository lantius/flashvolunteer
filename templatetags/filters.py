from google.appengine.ext import webapp
from django import template

register = webapp.template.create_template_register()

def team_status(parser, token):
    try:
        tag_name, account, account2 = token.split_contents()
    except ValueError:
        return None
    return RelationshipStatusNode(account = account, account2 = account2)

class RelationshipStatusNode(template.Node):
    def __init__(self, account, account2):
        self.account = account
        self.account2 = account2 
        
    def render(self, context):
        account = template.resolve_variable(self.account,context)
        try:
            account2 = template.resolve_variable(self.account2,context)
        except:
            context['is_teammate'] = False
            return ''
        if account:
            context['is_teammate'] = account.following.filter('follows =', account2).get() is not None
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
            mp = volunteer.account.message_preferences.filter('type =', message_type).get()
            if not mp: 
                prop = message_type.default_propagation
            else:
                prop = mp.propagation
            
            context['mt_checked'] = propagation_type.key().id() in prop
        return ''

register.tag(message_type_pref)
