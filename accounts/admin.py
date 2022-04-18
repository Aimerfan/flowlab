from django.contrib import admin

from .models import Student, Teacher


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Student._meta.fields]
    ordering = ['id']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Teacher._meta.fields]
    ordering = ['id']
