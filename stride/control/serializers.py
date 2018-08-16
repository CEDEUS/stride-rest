from django.contrib.auth.models import User, Group
from stride.control.models import Point, Observed, Data
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PuntoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Point
        fields = ('id', 'lat', 'lon', 'hdop', 'secuence', 'secuence_end', 'created_by', 'created_at', 'age', 'sex', 'ability', 'score', 'version')


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('id', 'observed', 'lat', 'lon', 'score', 'hdop')


class ObservedSerializer(serializers.ModelSerializer):
    data = DataSerializer(many=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Observed
        fields = ('id', 'created_by', 'created_at', 'updated_at', 'age', 'sex', 'ability', 'version', 'data')

    def create(self, validated_data):
        list_data = validated_data.pop('data')
        user =  self.context['request'].user
        validated_data['created_by'] = user
        instance = Observed.objects.create(**validated_data)
        for data in list_data:
            Data.objects.create(observed=instance, **data)
        return instance
