from django.contrib import admin
from stride.control.models import Point
from rest_framework.authtoken.admin import TokenAdmin


admin.site.register(Point)
TokenAdmin.raw_id_fields = ('user',)
