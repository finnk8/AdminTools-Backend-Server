# Generated by Django 5.0.4 on 2024-09-04 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divis', '0017_alter_father_child_alter_mother_child'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='teacher_error_message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
