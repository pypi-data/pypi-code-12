# -*- coding: utf-8 -*-

from django.db import models


class BigAutoField(models.AutoField):
    def db_type(self, connection):
        return 'bigserial'
