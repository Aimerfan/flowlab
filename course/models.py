from django.db import models

from core.models import Semester
from accounts.models import Teacher, Student
from flow.models import Project, Template


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
    students = models.ManyToManyField(Student, blank=True, verbose_name='學生')

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
    project = models.ManyToManyField(Project, blank=True)
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='套用模板',
    )
    branch = models.CharField('繳交分支', max_length=72)
    description = models.TextField('實驗描述', blank=True)
    deadline = models.DateTimeField('繳交期限', blank=True, null=True)

    class Meta:
        unique_together = ['course', 'name']
        verbose_name = verbose_name_plural = '實驗'

    def __str__(self):
        return f'{self.course.name}/{self.name}'


class Question(models.Model):
    QUESTION_TYPES = (
        ('text', '問答題'),
        ('single', '單選題'),
        ('multiple', '多選題'),
    )

    type = models.CharField('題目類型', max_length=50, choices=QUESTION_TYPES)
    content = models.CharField('題目內容', max_length=256)
    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        verbose_name='實驗',
    )
    number = models.DecimalField('編號', decimal_places=0, max_digits=3)

    class Meta:
        unique_together = ['lab', 'id']
        verbose_name = verbose_name_plural = '題目'

    def __str__(self):
        return f'{self.content}'


class Option(models.Model):
    content = models.CharField('選項內容', max_length=256)
    topic = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='題目',
    )
    number = models.DecimalField('編號', decimal_places=0, max_digits=2)

    class Meta:
        unique_together = ['topic', 'number']
        verbose_name = verbose_name_plural = '選項'

    def __str__(self):
        return f'{self.content}'


class Answer(models.Model):
    content = models.CharField('答案', max_length=256)
    topic = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='題目',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='學生',
    )

    class Meta:
        unique_together = ['content']
        verbose_name = verbose_name_plural = '答案'

    def __str__(self):
        return f'{self.content}'
