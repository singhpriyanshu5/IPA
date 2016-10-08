# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20160310_0644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewee',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='interviewee'),
        ),
    ]
