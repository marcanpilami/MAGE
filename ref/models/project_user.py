# coding: utf-8
""" model extending Django group authentication """

from django.db import models
from django.contrib.auth.models import User
from ref.models import Project


class ProjectUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, verbose_name='projects', related_name='project_user_projects')



