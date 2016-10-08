# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20160311_0654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewer',
            name='statusDesc',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='interviewer',
            name='user',
            field=models.OneToOneField(related_name='interviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]
