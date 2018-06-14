
# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-06-12 04:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zooniverse_web', '0002_insert_question_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questiondrawnresponse',
            unique_together=set([('response', 'survey_question')]),
        ),
        migrations.RemoveField(
            model_name='questiondrawnresponse',
            name='image',
        ),
    ]