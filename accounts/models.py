from enum import Enum

from django.db import models
from django.contrib.auth.models import User


# 每個繼承 RoleBaseModel 的類別都要在此註冊
class Role(Enum):
    STUDENT = 1
    TEACHER = 2


class RoleBaseModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='使用者')
    full_name = models.CharField('姓名', max_length=50, blank=True)

    class Meta:
        abstract = True


class Student(RoleBaseModel):
    class Meta:
        verbose_name = verbose_name_plural = '學生'

    def __str__(self):
        return self.full_name


class Teacher(RoleBaseModel):
    class Meta:
        verbose_name = verbose_name_plural = '教師'

    def __str__(self):
        return self.full_name
