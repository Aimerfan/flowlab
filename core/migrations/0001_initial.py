# Generated by Django 3.2.6 on 2021-12-07 19:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(max_length=4, unique=True, validators=[django.core.validators.RegexValidator('^\\d{3,4}[12]{1}$', 'Semester format validate error')], verbose_name='學期')),
                ('current', models.BooleanField(default=False, verbose_name='當前學期')),
            ],
            options={
                'verbose_name': '學期',
                'verbose_name_plural': '學期',
            },
        ),
    ]