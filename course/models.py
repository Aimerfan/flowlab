from django.db import models

from core.models import Semester
from accounts.models import Teacher


class Course(models.Model):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='學期',
    )
    name = models.CharField('課程名稱', max_length=50)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='指導老師',
    )

    class Meta:
        unique_together = ['semester', 'name']
        verbose_name = verbose_name_plural = '課程'

    def __str__(self):
        return f'{self.semester}/{self.name}'


class Lab(models.Model):
    name = models.CharField('實驗名稱', max_length=50)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='關聯課程',
    )
    branch = models.CharField('繳交分支', max_length=72)
    description = models.TextField('實驗描述', blank=True)
    deadline = models.DateTimeField('繳交期限', blank=True, null=True)
    # template = models.ForeignKey()

    class Meta:
        unique_together = ['course', 'name']
        verbose_name = verbose_name_plural = '實驗'

    def __str__(self):
        return f'{self.course.name}/{self.name}'
