# Generated by Django 3.2.10 on 2022-01-18 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flow', '0004_remove_project_labs'),
        ('course', '0004_course_students'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='project',
            field=models.ManyToManyField(blank=True, to='flow.Project'),
        ),
    ]
