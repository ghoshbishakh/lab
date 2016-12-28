# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-16 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_auto_20160616_0536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='websitesection',
            name='website_page',
        ),
        migrations.AddField(
            model_name='websitesection',
            name='section_type',
            field=models.CharField(choices=[('fixed', 'Fixed Section'), ('page', 'Page')], default='page', max_length=100),
        ),
        migrations.AddField(
            model_name='websitesection',
            name='show_in_nav',
            field=models.BooleanField(default=False),
        ),
    ]
