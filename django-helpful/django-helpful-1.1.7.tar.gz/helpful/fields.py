from django.db.models.fields.files import FieldFile


def file_type(filename):
	filename = filename.split('.')
	filetype = filename[len(filename) - 1].lower()
	if filetype == 'jpeg':
		filetype = 'jpg'
	return filetype

def upload_to(instance, filename):
	puth = ''

	if hasattr(instance, dependent_from):
		dependent_from = instance.dependent_from()
		puth += dependent_from._meta.app_label + '/'
		puth += dependent_from._meta.model_name + '/'
		puth += dependent_from.id + '/_'
		puth += instance._meta.model_name + '/'
	else:
		puth += instance._meta.app_label + '/'
		puth += instance._meta.model_name + '/'


	# Check for many fields
	file_fields = []
	for field_name, _ in instance.__dict__.iteritems():
		field = getattr(instance, field_name)
		if issubclass(field.__class__, FieldFile):
			file_fields.append(field_name)
		if field == filename:
			current_field_name = field_name

	# Prefix by field name
	if len(file_fields) > 1:
		puth += current_field_name + '_'

	# Name
	if hasattr(instance, 'slug'):
		name = instance.slug
	elif instance.id:
		name = '%s' % instance.id
	else:
		Model = instance.__class__
		if Model.objects.all():
			last = Model.objects.all().order_by('-id')[0]
			name = '%s' % (last.id + 1)
		else:
			name = '1'

	# Ext
	puth += name + '.'
	puth += file_type(filename)

	return puth
