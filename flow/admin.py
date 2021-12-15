from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']
    filter_horizontal = ('labs',)
    ordering = ['user']
