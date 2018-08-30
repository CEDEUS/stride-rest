
from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Point(models.Model):
    lat = models.DecimalField(max_digits=20, decimal_places=7)
    lon = models.DecimalField(max_digits=20, decimal_places=7)
    secuence = models.IntegerField(default=0)
    secuence_end = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    age = models.PositiveIntegerField(default=0)
    sex = models.CharField(max_length=2, default='N')
    ability = models.CharField(max_length=2, default='')
    score = models.CharField(max_length=2, default='')
    version = models.CharField(max_length=30, default='0.0.1', blank=True, null=True)
    hdop = models.FloatField(default=0.0, blank=True, null=True)

    def __unicode__(self):
        return '{} {} {}'.format(self.created_by.username, self.lon, self.lat)

class Observed(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    age = models.PositiveIntegerField(default=0)
    sex = models.CharField(max_length=2, default='N')
    ability = models.CharField(max_length=2, default='')
    version = models.CharField(max_length=30, default='0.0.1', blank=True, null=True)

class Data(models.Model):
    observed = models.ForeignKey(Observed, related_name='data', on_delete=models.SET_NULL, null=True)
    lat = models.DecimalField(max_digits=20, decimal_places=7)
    lon = models.DecimalField(max_digits=20, decimal_places=7)
    score = models.CharField(max_length=2, default='')
    hdop = models.FloatField(default=0.0, blank=True, null=True)


class Delete(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=2, null=True, blank=True)
    ability = models.CharField(max_length=2, null=True, blank=True)
    version = models.CharField(max_length=30, blank=True, null=True)

    def save(self, *args, **kwargs):
        observed = Observed.objects.all()
        if self.created_by:
            observed = observed.filter(created_by=self.created_by)
        if self.created_at:
            observed = observed.filter(created_at=self.created_at) # Revisar que fecha no compare por la hora sino que solo por el dia
        if self.age:
            observed = observed.filter(age=self.age)
        if self.sex:
            observed = observed.filter(sex=self.sex)
        if self.ability:
            observed = observed.filter(ability=self.ability)
        if self.version:
            observed = observed.filter(version=version)
        if observed != Observed.objects.all():
            for element in observed:
                element.delete()
        super(Delete, self).save()

