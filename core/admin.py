from django.contrib import admin

from .models import Semester


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Semester._meta.fields]
    ordering = ['-current', 'semester']
