# Generated by Django 5.0.4 on 2024-05-07 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divis', '0009_class_teacher_error_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schoolyear_prefix', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
    ]
