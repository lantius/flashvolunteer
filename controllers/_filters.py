from google.appengine.ext.webapp import template
from django.template import Library, Node, loader
from django.template.context import Context

register = template.create_template_register()

class PartialTemplateNode(Node):
	def __init__(self, template_name, context_item):
		self.template_name = template_name
		self.context_item = context_item

	def render(self, context):
		template = loader.get_template('partials/%s.html' % (self.template_name,))
		item = self.context_item.resolve(context)
		template_context = Context({
			'item': item
		})
		return template.render(template_context)

@register.tag
def partial_template(parser, token):
	tag, template_name, context_item = token.split_contents()
	return PartialTemplateNode(template_name, context_item)


@register.filter
def cut(value, arg):
  return value.replace(arg, '')