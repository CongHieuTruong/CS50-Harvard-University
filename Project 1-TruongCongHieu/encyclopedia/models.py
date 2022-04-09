from cgitb import text
from email.mime import image
from turtle import title
from django.db import models

# Create your models here.

class FormModel(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    image = models.ImageField(upload_to='images/', verbose_name="", blank=True)
    def __str__(self):
        return self.title