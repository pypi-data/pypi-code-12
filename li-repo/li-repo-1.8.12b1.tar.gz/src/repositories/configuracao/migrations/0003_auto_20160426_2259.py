# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envio',
            name='imagem',
            field=models.CharField(default=None, max_length=255, null=True, db_column=b'envio_imagem'),
        ),
        migrations.AlterField(
            model_name='parcela',
            name='fator',
            field=models.DecimalField(null=True, decimal_places=6, max_digits=16, db_column=b'pagamento_parcela_fator'),
        ),
    ]
