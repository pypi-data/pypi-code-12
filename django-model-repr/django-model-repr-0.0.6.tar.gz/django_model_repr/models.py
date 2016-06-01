# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings

class Model(models.Model):
	class Meta:
		abstract = True

	def __repr__(self):
		fields = self._meta.get_fields()
		classname = self.__class__.__name__
		exclude = getattr(settings, "MODEL_REPR_EXCLUDE", {}).get(classname, [])

		buf = "<%s"%(classname)
		buf += "\n"

		for field in fields:
			if not field.concrete or field in exclude:
				continue

			buf += "\t%s: %s"%(field.name, getattr(self, field.name))
			buf += "\n"

		buf += ">"

		return buf


if getattr(settings, "MODEL_REPR_MONEY_PATCHING", True):
	setattr(models, "Model", Model)
