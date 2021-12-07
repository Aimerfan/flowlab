from django.db import models, transaction
from django.core.validators import RegexValidator


class Semester(models.Model):
    semester = models.CharField(
        '學期', max_length=4, unique=True,
        validators=[
            RegexValidator(r'^\d{3,4}[12]{1}$', 'Semester format validate error'),
        ])
    current = models.BooleanField('當前學期', default=False)

    class Meta:
        verbose_name = verbose_name_plural = '學期'

    def __str__(self):
        return self.semester

    def save(self, *args, **kwargs):
        if self.current:
            # 修改其他期別 當前期程 欄位
            with transaction.atomic():
                Semester.objects.filter(current=True).update(current=False)
        return super().save(*args, **kwargs)
