from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from stride.control.models import Point, Observed, Data
from stride.control.serializers import PuntoSerializer, DataSerializer, ObservedSerializer, MyDataSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.shortcuts import render

class PuntoViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Point.objects.all()
    serializer_class = PuntoSerializer

    my_filter_fields = ('lat', 'lon', 'created_by', 'created_at', 'hdop', 'age', 'sex', 'ability', 'version', 'secuence')

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(PuntoViewSet, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_kwargs_for_filtering(self):
        filtering_kwargs = {}

        for field in  self.my_filter_fields:
            field_value = self.request.query_params.get(field)
            if field_value:
                filtering_kwargs[field] = field_value
        return filtering_kwargs

    def get_queryset(self):
        queryset = Point.objects.all()

        filtering_kwargs = self.get_kwargs_for_filtering()
        if filtering_kwargs:
            queryset = Point.objects.filter(**filtering_kwargs)

        return queryset


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class DanielViewSet(viewsets.ModelViewSet):

    queryset = Point.objects.all()
    serializer_class = PuntoSerializer

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(PuntoViewSet, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ObservedViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication, JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Observed.objects.all()
    serializer_class = ObservedSerializer

    my_filter_fields = ('created_by', 'created_at', 'age', 'sex', 'ability', 'version', 'created_by__username', 'created_at__gte', 'created_at__lte', 'created_at__gt', 'created_at__lt')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_kwargs_for_filtering(self):
        filtering_kwargs = {}

        for field in  self.my_filter_fields:
            field_value = self.request.query_params.get(field)
            if field_value:
                filtering_kwargs[field] = field_value
        return filtering_kwargs

    def get_queryset(self):
        queryset = Observed.objects.all()

        filtering_kwargs = self.get_kwargs_for_filtering()
        if filtering_kwargs:
            queryset = Observed.objects.filter(**filtering_kwargs)

        return queryset

class MyDataViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication, JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Data.objects.all()
    serializer_class = MyDataSerializer

    my_filter_fields = ('count',)

    def get_kwargs_for_filtering(self):
        filtering_kwargs = {}

        for field in  self.my_filter_fields:
            field_value = self.request.query_params.get(field)
            if field_value:
                filtering_kwargs[field] = field_value
        return filtering_kwargs

    def get_queryset(self):
        queryset = Data.objects.all()
        last_count = 200

        filtering_kwargs = self.get_kwargs_for_filtering()
        if filtering_kwargs:
            last_count = int(filtering_kwargs['count'])
        queryset = queryset.filter(observed__created_by=self.request.user)[:last_count]

        return queryset

class DataViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication, JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Data.objects.all()
    serializer_class = DataSerializer

def TablaDatos(request):
    delete_data = request.GET.get('d', list())
    delete_data = delete_data if isinstance(delete_data, list) else delete_data.split(',')
    for delete in delete_data:
        if len(Data.objects.filter(id=delete)) > 0:
            Data.objects.get(id=delete).delete()
    datos = Data.objects.all()
    return render(request, 'table.html', {'datos': datos})
