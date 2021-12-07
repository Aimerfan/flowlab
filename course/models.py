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
