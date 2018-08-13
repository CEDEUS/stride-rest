from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from stride.control.models import Point, Observed, Data
from stride.control.serializers import UserSerializer, GroupSerializer, PuntoSerializer, DataSerializer, ObservedSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


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

    queryset = Observed.objects.all()
    serializer_class = ObservedSerializer

    def create(self, request, *args, **kwargs):
        #request.data['user'] = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
