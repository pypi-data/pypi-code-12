from django.db import models

"""
	@name: OAthToken
	@author: exile.sas
	@date: 27/06/2016
	@licence: creative commons
"""
class OAuthToken(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	token = models.CharField(max_length=120)

# end class

