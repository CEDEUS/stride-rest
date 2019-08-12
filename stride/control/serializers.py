from django.contrib.auth import get_user_model, authenticate
from stride.control.models import Point, Observed, Data, UserStadistic
from rest_framework import serializers

from djoser import constants, utils
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

from datetime import datetime, timedelta, time
from django.utils import timezone

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    total_observed_person = serializers.SerializerMethodField()
    total_points_voted = serializers.SerializerMethodField()
    today_observed_person = serializers.SerializerMethodField()
    days_surveyed = serializers.SerializerMethodField()
    today_points = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
            'date_joined',
            'groups',
            'total_observed_person',
            'total_points_voted',
            'today_observed_person',
            'days_surveyed',
            'today_points',
        )
        read_only_fields = (User.USERNAME_FIELD, 'total_observed_person', 'total_points_voted', 'today_observed_person', 'date_joined', 'groups', 'days_surveyed', 'today_points')

    def get_total_observed_person(self, obj):
        return len(Observed.objects.filter(created_by=obj))

    def get_today_observed_person(self, obj):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        stadistic, created = UserStadistic.objects.get_or_create(user=obj, tag='today_observed_person')
        return len(Observed.objects.filter(created_by=obj, created_at__lte=today_end, created_at__gte=today_start))

    def get_total_points_voted(self, obj):
        return len(Data.objects.filter(observed__created_by=obj))

    def get_days_surveyed(self, obj):
        obs = Observed.objects.filter(created_by=obj)
        days = list()
        for ob in obs:
            days.append(ob.created_at.date())
        return len(list(set(days)))

    def get_today_points(self, obj):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        count = 0
        all_observed = Observed.objects.filter(created_by=obj, created_at__lte=today_end, created_at__gte=today_start)
        for obs in all_observed:
            count += len(Data.objects.filter(observed=obs))
        return count

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super(UserSerializer, self).update(instance, validated_data)


class PuntoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Point
        fields = ('id', 'lat', 'lon', 'hdop', 'secuence', 'secuence_end', 'created_by', 'created_at', 'age', 'sex', 'ability', 'score', 'version')


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('id', 'observed', 'category', 'lat', 'lon', 'score', 'hdop')


class MyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        ordering = ('-id',)
        fields = ('id', 'observed', 'category', 'lat', 'lon', 'score', 'hdop')


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS)+ (User.USERNAME_FIELD,)
        read_only_fields = (User.USERNAME_FIELD, )


class ObservedSerializer(serializers.ModelSerializer):
    data = DataSerializer(many=True)
    created_by = UsernameSerializer(read_only=True)

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
