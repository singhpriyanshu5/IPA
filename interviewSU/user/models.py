from django.db import models
from django.contrib.auth.models import User


class InterviewGroup(models.Model):
    name = models.CharField(max_length=50)
    maxRegister = models.IntegerField()
    closeSelection = models.IntegerField()

    def __str__(self):
        return self.name


class InterviewDepartment(models.Model):
    name = models.CharField(max_length=50)
    # code = models.CharField(max_length=50)
    group = models.ForeignKey(InterviewGroup, related_name="department")
    queueNow = models.IntegerField(default=0)
    queueLast = models.IntegerField(default=0)
    customQuestion = models.CharField(max_length=1000, blank=True)
    # failMessage = models.TextField(max_length=2000, blank=True)
    # successMessage = models.TextField(max_length=2000, blank=True)

    def __str__(self):
        return self.name


class Interviewee(models.Model):
    user = models.OneToOneField(User, related_name="interviewee")
    name = models.CharField(max_length=100)
    matricNumber = models.CharField(max_length=50)
    year = models.IntegerField()
    major = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    countAccepted = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def hitung(self):
        cnt = 0
        for q in self.interviewRegister.all():
            if q.resultPending == 1:
                cnt += 1
        return cnt


class InterviewRegister(models.Model):
    interviewee = models.ForeignKey(Interviewee, related_name="interviewRegister")
    department = models.ForeignKey(InterviewDepartment, related_name="interviewRegister")
    queueNumber = models.IntegerField()
    # TODO: remove magic number
    status = models.IntegerField()
    customAnswer = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    lastAction = models.DateTimeField(auto_now=True)
    resultPending = models.IntegerField(default=0)
    resultFinal = models.IntegerField(default=0)

    def __str__(self):
        return self.department.name


class Interviewer(models.Model):
    user = models.OneToOneField(User, related_name="interviewer")
    department = models.ForeignKey(InterviewDepartment, related_name="interviewer")
    # code = models.CharField(max_length=50)
    # TODO: remove magic number
    status = models.IntegerField(default=0)
    statusDesc = models.IntegerField(default=-1)
    lastAction = models.DateTimeField(auto_now=True)


class Boss(models.Model):
    user = models.OneToOneField(User, related_name="boss")
    group = models.ForeignKey(InterviewGroup, related_name="boss")
