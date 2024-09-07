from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from files.models import UploadedFile
from .models import Teacher, Student, Class, Settings
from .serializers import TeacherSerializer, StudentSerializer, ClassSerializer, SettingsSerializer
from .utils import process_divis_teacher_csv, process_divis_classes_csv

class SettingsViewSet(ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = '__all__'
    search_fields = ('first_name', 'last_name', 'abbreviation')

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = '__all__'
    search_fields = ('first_name', 'last_name', 'class_name')

class ClassViewSet(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = '__all__'
    search_fields = ('name',)

@api_view(['POST'])
@csrf_exempt
def upload_teacher_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Speichern der Datei in der Datenbank
        uploaded_file_object = UploadedFile.objects.create(file=uploaded_file)
        # Prozessierung der Datei
        return process_divis_teacher_csv(uploaded_file_object.file.name, request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')
    

@api_view(['POST'])
@csrf_exempt
def upload_classes_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Save the uploaded file to the database
        uploaded_file_object = UploadedFile.objects.create(file=uploaded_file)
        # Process the file
        return process_divis_classes_csv(uploaded_file_object.file.name, request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')