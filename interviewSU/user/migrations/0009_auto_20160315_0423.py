# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_interviewee_countaccepted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interviewee',
            old_name='countaccepted',
            new_name='countAccepted',
        ),
    ]
