from django.contrib.auth.models import User, Group
from stride.control.models import Point
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PuntoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Point
        fields = ('id', 'lat', 'lon', 'secuence', 'created_by', 'created_at', 'age', 'sex', 'ability', 'score')
