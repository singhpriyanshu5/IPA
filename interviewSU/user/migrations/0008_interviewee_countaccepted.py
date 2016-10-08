# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20160314_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewee',
            name='countaccepted',
            field=models.IntegerField(default=0),
        ),
    ]
