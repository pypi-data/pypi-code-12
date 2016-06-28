
"""
	@name: SupraOAth
	@author: exile.sas
	@date: 27/06/2016
	@licence: creative commons
"""
class SupraOAth(object):
	def __call__(self, request):
		from models import OAthToken
		if 'HTTP_AUTHORIZATION' in request.META:
			token = request.META['HTTP_AUTHORIZATION']
			token = OAthToken.objects.filter(token=token).first()
			if token:
				return None
			# end if
		# end if
		from django.core.exceptions import PermissionDenied
		raise PermissionDenied
	# end def
# end def
