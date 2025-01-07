from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    default_view = models.CharField(max_length=100)

class Assignment(models.Model):
    class AssignmentStatus(models.TextChoices):
        Todo="To do", "To do"
        InProgress="In Progress", "In Progress"
        Completed="Completed", "Completed"
    
    title = models.CharField(max_length=100)
    assignment_class = models.CharField(max_length=100)
    assignment_status = models.CharField(max_length=15,
                                         default="To do")
    deadline = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Course(models.Model):
    roster = models.ManyToManyField(User)
    course_name = models.CharField(max_length=200)
    courseid = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.course_name

class Note(models.Model):
    lecture = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    #doc = models.FileField(upload_to='media/')

class ClassNote(models.Model):
    title = models.CharField(max_length=200)
    pdf = models.FileField(upload_to='media/')
    lecture = models.ForeignKey(Course, on_delete=models.CASCADE)

class ClassNotes(models.Model):
    title = models.CharField(max_length=200)
    pdf = models.FileField(upload_to='media/')
    notes_class = models.ForeignKey(Course, on_delete=models.CASCADE)
