from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from django.conf.urls import url, include
from rest_framework import routers
from stride.control import views

router = routers.DefaultRouter()
router.register(r'points', views.PuntoViewSet)
router.register(r'daniel', views.DanielViewSet)
router.register(r'observed', views.ObservedViewSet)

admin.autodiscover()


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.CustomAuthToken.as_view()),
    url(r'^obtain_token/', obtain_jwt_token),
    url(r'^refresh_token/', refresh_jwt_token),
    re_path(r'^api/', include('djoser.urls')),
    re_path(r'^api/', include('djoser.urls.jwt')),
]
