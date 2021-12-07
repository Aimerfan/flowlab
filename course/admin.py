from django.contrib import admin

from .models import Course, Lab


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Course._meta.fields]


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lab._meta.fields]
