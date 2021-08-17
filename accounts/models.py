from django.db import models
from django.contrib.auth.models import User


class RoleBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='使用者')
    full_name = models.CharField('姓名', max_length=50, blank=True)

    class Meta:
        abstract = True


class Student(RoleBase):
    class Meta:
        verbose_name = verbose_name_plural = '學生'


class Teacher(RoleBase):
    class Meta:
        verbose_name = verbose_name_plural = '教師'
