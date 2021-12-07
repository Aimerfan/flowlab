from django.contrib import admin

from .models import Course, Lab


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'semester', 'name', 'teacher')
    filter_horizontal = ('students',)


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lab._meta.fields]
