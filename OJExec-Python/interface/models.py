from shutil import rmtree
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone as t
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from accounts.models import Coder

TEST_CASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Programming_Language(models.Model):
    name = models.CharField(max_length=16)
    ext = models.CharField(max_length=16)
    compile_command = models.CharField(max_length=255)
    run_command = models.CharField(max_length=255)
    multiplier_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name 


class Contest(models.Model):
    contest_name = models.TextField(help_text="Name of Contest", blank=True)
    contest_code = models.TextField(blank=True, help_text="Code for Contest")
    contest_image = models.ImageField(upload_to="contest_images/", blank=True, null=True)
    start_time = models.DateTimeField(default=t.now, help_text="Start time for contest")
    end_time = models.DateTimeField(default=t.now, help_text="End time for contest")
    contest_langs = models.ManyToManyField(Programming_Language)

    def __str__(self):
        return self.contest_name + " " + self.contest_code

    def isStarted(self):
        return (t.now() > self.start_time and t.now() < self.end_time)

    def isOver(self):
        return (t.now() > self.end_time and t.now() > self.start_time)

    class Meta:
        ordering = ['end_time']

class Job(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    coder = models.ForeignKey(Coder, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, help_text="Name goes here")
    question_name = models.CharField(max_length=200, null=True, help_text="Question Name goes here")
    code = models.TextField(blank=True, help_text="Code goes here")
    lang = models.CharField(max_length=100, blank=True, help_text="language of the code")
    status = models.TextField(blank=True, help_text="Status in json format. Please don't touch it.")
    AC_no = models.IntegerField(default=0, help_text="Number of correct answers for this job")
    WA_no = models.IntegerField(default=0, help_text="Number of wrong answers for this job")
    job_id = models.CharField(max_length=200, null=True, unique=True, help_text="Celery Job id for the current task")
    timestamp = models.DateTimeField(default=t.now, help_text="Latest submission")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.id + " " + self.coder.name


