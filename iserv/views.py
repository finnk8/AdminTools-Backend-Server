from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.shortcuts import HttpResponse

from files.models import UploadedFile
from .models import IservGroup, ExistingAccount
from .serializers import IservGroupSerializer, ExistingAccountSerializer
from .utils import process_iserv_exported_users_csv, process_iserv_accounts_for_duplicates

class IservGroupViewSet(ModelViewSet):
    queryset = IservGroup.objects.all()
    serializer_class = IservGroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = '__all__'
    search_fields = ('name',)

class ExistingAccountViewSet(ModelViewSet):
    queryset = ExistingAccount.objects.all()
    serializer_class = ExistingAccountSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = '__all__'
    search_fields = ('account', 'first_name', 'last_name', 'internal_id')

@csrf_exempt
def upload_account_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # speichern der Datei in der Datenbank
        uploaded_file_object = UploadedFile.objects.create(file=uploaded_file)
        # Prozessierung der Datei
        return process_iserv_exported_users_csv(uploaded_file_object.file.name)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')
    
@api_view(['POST'])
@csrf_exempt
def check_for_duplicates(request):
    if request.method == 'POST':
        return process_iserv_accounts_for_duplicates(request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')