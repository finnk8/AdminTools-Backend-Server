# Generated by Django 5.0.4 on 2024-09-06 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divis', '0018_alter_class_teacher_error_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='iserv_account',
            field=models.IntegerField(blank=True, max_length=100, null=True),
        ),
    ]
