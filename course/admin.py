from django.contrib import admin

from .models import Course, Lab, Question, Option, Answer


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'semester', 'name', 'teacher')
    filter_horizontal = ('students',)


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lab._meta.fields]
    filter_horizontal = ('project',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab', 'type', 'content')
    ordering = ['lab', 'number']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'number', 'content')
    ordering = ['topic', 'number']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'topic', 'content')
    ordering = ['topic']
