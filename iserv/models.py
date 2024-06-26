from django.db import models

# Create your models here.
class IservGroup(models.Model):
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return self.group_name

class ExistingAccount(models.Model):
    account = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    internal_id = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=100, blank=True, null=True)
    import_id = models.CharField(max_length=100, blank=True, null=True)
    class_information = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(IservGroup, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.internal_id + ')'