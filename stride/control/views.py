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

import csv
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


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
        #bbox = self.request.query_params.get('bbox', None)
        #if bbox is not None:
        #    cords = bbox.split(',')
        #    if len(cords)==4:
        #        minlat, minlon, maxlat, maxlon = cords
        #        queryset = queryset.filter(ubicacion__lat__gte=minlat, ubicacion__lon__gte=minlon, ubicacion__lat__lte=maxlat, ubicacion__lon__lte=maxlon)
        return queryset

    #@method_decorator(cache_page(60*60*2))
    #def get(self, request, format=None):
    #    return super().get(request, format)


class ObservedViewSetNoPagination(ObservedViewSet):
    pagination_class = None


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
    bbox_str = request.GET.get('bbox', None)
    if bbox_str:
        bbox = bbox_str.split(',')
        min_lat, min_lon, max_lat, max_lon = bbox
        datos = datos.filter(lat__gte=min_lat, lat__lte=max_lat, lon__gte=min_lon, lon__lte=max_lon)
    return render(request, 'table.html', {'datos': datos})

@csrf_exempt
def csvResponse(request):
    if request.method == 'POST':
        ids = request.POST.get('csv', '')
        ids = ids.split(',') if ids else []
        all_ids = [int(x) for x in ids]
        query = Data.objects.filter(id__in=all_ids)
        all = request.POST.get('all', False)
        if all:
            query = Data.objects.all()
        # header_csv = ['id', 'observed__created_by', 'observed__created_at', 'observed__age', 'observed__sex', 'observed__ability', 'lat', 'lon','hdop', 'score', 'category']
        header_csv = ['id', 'created_by', 'created_at', 'age', 'sex', 'ability', 'category', 'lat', 'lon', 'score']

        filename = 'Data-{}.csv'.format(datetime.datetime.today().strftime("%Y-%m-%dT%H-%M-%S"))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        writer = csv.writer(response)
        writer.writerow(header_csv)
        for q in query:
            new_row = [q.id, q.observed.created_by, q.observed.created_at, q.observed.age, q.observed.sex, q.observed.ability, q.category, q.lat, q.lon, q.score]
            new_row2 = [str(x) for x in new_row]
            writer.writerow(new_row2)
        return response
    else:
        return HttpResponse("GET method not acepted.. @csfuente will punish you", content_type="text/plain")

