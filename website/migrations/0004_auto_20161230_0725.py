# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 07:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0003_auto_20161229_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('identifier', models.SlugField(max_length=100, unique=True)),
                ('body', models.TextField()),
                ('posted', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='websitesection',
            name='website_position_id',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]