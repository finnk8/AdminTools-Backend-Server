from django.db import models
from iserv.models import ExistingAccount

# Create your models here.
class Settings(models.Model):
    schoolyear_prefix = models.CharField(max_length=10, blank=True, null=True)
    clear_existing_data = models.BooleanField(default=False)

class Teacher(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    birth_date = models.CharField(max_length=100, blank=True, null=True)
    abbreviation = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.abbreviation + ')'

class Student(models.Model):
    iserv_account = models.IntegerField(max_length=100, blank=True, null=True)

    last_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    birth_date = models.CharField(max_length=15, blank=True, null=True)
    class_name = models.CharField(max_length=10, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    eduport_mail = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.class_name + ')'
    
class Mother(models.Model):
    child = models.CharField(max_length=100, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Father(models.Model):
    child = models.CharField(max_length=100, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Class(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    iserv_group_name = models.CharField(max_length=100, blank=True, null=True)
    teacher = models.CharField(max_length=100, blank=True, null=True)
    teacher_error_message = models.CharField(max_length=100, blank=True, null=True)
    students = models.ManyToManyField(Student, blank=True, related_name='classes')

    def __str__(self):
        return self.name