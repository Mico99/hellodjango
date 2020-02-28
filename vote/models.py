from django import forms
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from vote.forms import USERNAME_PATTERN, to_md5_hex


class User(models.Model):
    """用户"""
    no = models.AutoField(primary_key=True, verbose_name='编号')
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')
    regdate = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    def __str__(self):
        return "vote %s" % self.username

    class Meta:
        db_table = 'tb_user'
        verbose_name_plural = '用户'
        app_label = 'vote'


class Subject(models.Model):
    """学科"""
    no = models.IntegerField(primary_key=True, verbose_name='编号')
    name = models.CharField(max_length=20, verbose_name='名称')
    intro = models.CharField(max_length=511, default='', verbose_name='介绍')
    create_date = models.DateField(null=True, verbose_name='成立日期')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')

    def __str__(self):
        return "vote %s" % self.name

    class Meta:
        db_table = 'tb_subject'
        verbose_name = '学科'
        verbose_name_plural = '学科'
        app_label = 'vote'


class Teacher(models.Model):
    no = models.AutoField(primary_key=True, verbose_name='编号')
    name = models.CharField(max_length=20, verbose_name='姓名')
    detail = models.CharField(max_length=1023, default='', blank=True, verbose_name='详情')
    photo = models.CharField(max_length=1023, default='', verbose_name='照片')
    good_count = models.IntegerField(default=0, verbose_name='好评数')
    bad_count = models.IntegerField(default=0, verbose_name='差评数')
    subject = models.ForeignKey(to=Subject, on_delete=models.PROTECT, db_column='sno', verbose_name='所属学科')

    def __str__(self):
        return "vote %s" % self.name

    class Meta:
        db_table = 'tb_teacher'
        verbose_name = '老师'
        verbose_name_plural = '老师'
        app_label = 'vote'


class LoginForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=20)
    password = forms.CharField(min_length=8, max_length=20)
    captcha = forms.CharField(min_length=4, max_length=4)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValidationError('无效的用户名')
        return username

    def clean_password(self):
        return to_md5_hex(self.cleaned_data['password'])
