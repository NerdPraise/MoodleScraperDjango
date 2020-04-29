from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=False)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    BASIC = 'BC'
    BIG_BOSS = 'BB'
    NONE = "NN"

    CHOICE_PLAN = [(BASIC, "BASIC"), (BIG_BOSS, "BIG BOSS"), (NONE,"NONE")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=1)
    paid = models.BooleanField(default=False)
    plan = models.CharField(max_length=2, choices=CHOICE_PLAN, default=NONE)


    def __str__(self):
        return "{}".format(self.user.username)


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=80)
    course_url = models.URLField(max_length=1500)
    refresh_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.course_name)


class MoodleDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Moodle Details"

@receiver(post_save, sender=User)
def update_user_profile(sender,created, instance, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()