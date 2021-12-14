from django.db import models
from django.contrib.auth.models import User

from course.models import Course


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    # 格式限制必須要跟 .form.BaseRepoForm.name 同步
    name = models.CharField('專案名稱', max_length=50)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='關聯課程',
    )
    # TODO: 分組功能
    # group = models.BooleanField

    class Meta:
        unique_together = ['user', 'name']
        verbose_name = verbose_name_plural = '專案'

    def __str__(self):
        return f'{self.user}/{self.name}'
