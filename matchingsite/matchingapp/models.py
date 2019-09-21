from django.db import models
import datetime
from django.contrib.auth.models import User



class Hobby(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Profile(models.Model):
    text = models.CharField(max_length=4096, blank=True)
    image = models.ImageField(upload_to='media/', blank=True)


    @property
    def has_member(self):
        return hasattr(self, 'member') and self.member is not None

    # Either the username of the Member, or NONE
    @property
    def member_check(self):
        return str(self.member) if self.has_member else 'NONE'

    def __str__(self):
        return self.text + ' (' + self.member_check + ')'

class Member(User):
    # https://docs.djangoproject.com/en/2.1/ref/contrib/auth/
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(max_length=8)
    profile = models.OneToOneField(
        to=Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    hobby = models.ManyToManyField(
    to=Hobby,
    blank=True,
    )

    def __str__(self):
        return self.username
