from datetime import date

from django.db import models
from django.contrib.auth.models import User

from accounts.models import Teacher


def upload_to_path(instance, filename):
    return f'templates/{instance}'


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    # 格式限制必須要跟 .form.BaseRepoForm.name 同步
    name = models.CharField('專案名稱', max_length=50)
    # TODO: 分組功能
    # group = models.BooleanField

    class Meta:
        unique_together = ['user', 'name']
        verbose_name = verbose_name_plural = '專案'

    def __str__(self):
        return f'{self.user}/{self.name}'


class Template(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='擁有者',
    )
    name = models.CharField('模板名稱', max_length=50)
    template = models.FileField('模板檔案', upload_to=upload_to_path)
    date = models.DateField('建立日期', default=date.today)

    class Meta:
        unique_together = ['teacher', 'name']
        verbose_name = verbose_name_plural = '模板'

    def __str__(self):
        return f'{self.teacher}/{self.name}'
