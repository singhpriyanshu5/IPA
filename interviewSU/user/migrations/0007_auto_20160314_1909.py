# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_boss'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewee',
            name='user',
            field=models.OneToOneField(related_name='interviewee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='interviewer',
            name='user',
            field=models.OneToOneField(related_name='interviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]
