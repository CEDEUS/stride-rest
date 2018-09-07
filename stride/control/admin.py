from django.contrib import admin
from stride.control.models import Point, Observed, Data, Delete
from rest_framework.authtoken.admin import TokenAdmin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin


admin.site.register(Point)
TokenAdmin.raw_id_fields = ('user',)
admin.site.register(Observed)
admin.site.register(Delete)

class DataResource(resources.ModelResource):
    class Meta:
        model = Data
        fields = ('id', 'observed__created_by', 'observed__created_at', 'observed__age', 'observed__sex', 'observed__ability', 'lat', 'lon','hdop', 'score', 'observed__version')

class DataAdmin(ImportExportModelAdmin):
    resource_class = DataResource

class DataAdminF(ImportExportActionModelAdmin):
    pass

admin.site.register(Data, DataAdmin)
