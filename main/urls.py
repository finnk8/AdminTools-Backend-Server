from django.contrib import admin
from django.urls import include, path

from iserv.views import upload_account_data, check_for_duplicates
from divis.views import upload_teacher_data, upload_classes_data

from .test import download_iserv_import

# Customizing Admin panel
admin.site.site_header = 'Admin Tools - Datenbank'
admin.site.site_title = 'Admin Tools - Datenbank'

urlpatterns = [
    # Admin panel and API authentication
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')), # URL für die Authentifizierung
    path('auth/', include('djoser.urls.jwt')), # URL für die Authentifizierung

    # API endpoints
    path('divis/', include('divis.urls')),
    path('iserv/', include('iserv.urls')),

    # File upload and processing endpoints
    path('upload/iserv/accounts', upload_account_data),
    path('upload/divis/teachers', upload_teacher_data),
    path('upload/divis/classes', upload_classes_data),
    path('process/check-for-duplicates', check_for_duplicates),

    # Generate CSV file from database data
    path('download/iserv/importfile', download_iserv_import),
]
