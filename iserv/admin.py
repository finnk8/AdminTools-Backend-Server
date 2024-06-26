from django.contrib import admin
from .models import IservGroup, ExistingAccount


# Register your models here.
@admin.register(IservGroup)
class IservGroupsAdmin(admin.ModelAdmin):
    pass

@admin.register(ExistingAccount)
class ExistingAccountsAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'internal_id', 'account')