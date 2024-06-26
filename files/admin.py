from django.contrib import admin
from .models import UploadedFile

# Register your models here.
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    pass