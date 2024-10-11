from django.db import models

# Create your models here.
# 在models.py中定义模型
class UserInfo(models.Model):
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=128)
    age = models.IntegerField()
