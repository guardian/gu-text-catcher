from google.appengine.ext.webapp import template

register = template.create_template_register()
@register.filter(name='nice_timestamp')
def nice_timestamp(datetime):
	return datetime.strftime("%H:%M:%S %d/%m/%Y")