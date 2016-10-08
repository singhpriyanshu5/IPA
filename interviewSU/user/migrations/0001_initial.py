# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Boss',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='InterviewDepartment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=50)),
                ('queueNow', models.IntegerField(default=0)),
                ('queueLast', models.IntegerField(default=0)),
                ('customQuestion', models.CharField(max_length=1000, blank=True)),
                ('failMessage', models.TextField(max_length=2000, blank=True)),
                ('successMessage', models.TextField(max_length=2000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Interviewee',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('matricNumber', models.CharField(max_length=50)),
                ('year', models.IntegerField()),
                ('major', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='interviewee')),
            ],
        ),
        migrations.CreateModel(
            name='Interviewer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('status', models.IntegerField(default=0)),
                ('statusDesc', models.CharField(max_length=50, blank=True)),
                ('lastAction', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(to='user.InterviewDepartment', related_name='interviewer')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='interviewer')),
            ],
        ),
        migrations.CreateModel(
            name='InterviewGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('maxRegister', models.IntegerField()),
                ('closeSelection', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InterviewRegister',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('customAnswer', models.TextField(blank=True)),
                ('status', models.IntegerField()),
                ('queueNumber', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('score', models.IntegerField(default=0)),
                ('lastAction', models.DateTimeField(auto_now=True)),
                ('resultPending', models.IntegerField(default=0)),
                ('resultFinal', models.IntegerField(default=0)),
                ('department', models.ForeignKey(to='user.InterviewDepartment', related_name='interviewee')),
                ('interviewee', models.ForeignKey(to='user.Interviewee', related_name='interviewRegister')),
            ],
        ),
        migrations.AddField(
            model_name='interviewdepartment',
            name='group',
            field=models.ForeignKey(to='user.InterviewGroup', related_name='department'),
        ),
        migrations.AddField(
            model_name='boss',
            name='group',
            field=models.ForeignKey(to='user.InterviewGroup', related_name='boss'),
        ),
    ]
