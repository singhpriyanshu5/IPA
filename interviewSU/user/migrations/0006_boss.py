# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0005_auto_20160314_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('group', models.ForeignKey(to='user.InterviewGroup', related_name='boss')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='boss')),
            ],
        ),
    ]
