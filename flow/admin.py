from django.contrib import admin

from .models import Project, Template


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']
    # filter_horizontal = ('labs',)
    ordering = ['user']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'name']
    ordering = ['teacher']
