from google.appengine.ext import webapp
from django import template

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