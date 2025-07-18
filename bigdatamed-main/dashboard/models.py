from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.db.models.fields import DateField
from django.db.models.fields.files import ImageField
# Create your models here.

class Profile(models.Model):
    user      = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    image     = models.ImageField(upload_to ="uploads/profile/")
    address   = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)
    skill     = RichTextField(default="",blank=True, null=True)
    bio       = RichTextField(default="",blank=True, null=True)


    def __str__(self):
        return str(self.user)

class Category(models.Model):
    name        = models.CharField(max_length=255, null=True, blank=True)
    url         = models.URLField(max_length = 200)
    image       = models.ImageField(upload_to="uploads/category/")
    description = RichTextField(default="",blank=True, null=True)

    def __str__(self):
        return str(self.name)

class ProblemSelection(models.Model):
    name        = models.CharField(max_length=255, null=True, blank=True)
    url         = models.URLField(max_length = 200)
    image       = models.ImageField(upload_to="uploads/problemSelection/")
    description = RichTextField(default="",blank=True, null=True)

    def __str__(self):
        return str(self.name)

"""
Models data experiment for user
    @params:
        - user:         User that belong to this experiment
        - date_create:  Date when create this experiment
        - name_bbdd:    Name data base where it extract this dataset
        - date_init:    Date start partition dataset
        - date_end:     Date end partition dataset
        - filter_apply: Columns selected of  dataset
"""
class Experiment(models.Model):
    user            = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    date_create     = models.DateField(auto_now=True)
    name            = models.CharField(max_length=255,null=True,blank=True)
    name_bbdd       = models.CharField(max_length=255,null=True,blank=True)
    date_init       = models.DateField(null=True,blank=True)
    date_end        = models.DateField(null=True,blank=True)
    filter_apply    = models.CharField(max_length=10000,null=True,blank=True)

    def __str__(self):       
        return str(self.date_create) + " / " + str(self.name)
"""
Models DataBaseSystem
    This model should is harmony with the database from api of our aplication. 
    For example: If code is EPI and name Epidimiology, 
    in our api we will work with code EPI and depend this code its execute way. 
    @params:
        - code:         Database code. It's important that it was the same that code from our api.
        - name:         Database name. This name will show in dropdown select  our aplication. 
"""

class DataBaseSystem(models.Model):
    code = models.CharField(max_length=5, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):       
        return str(self.code) + " -  " + str(self.name)

   







