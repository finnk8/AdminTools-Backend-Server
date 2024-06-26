from django.contrib import admin
from .models import Teacher, Student, Class, Mother, Father

# Register your models here.

class ClassInline(admin.TabularInline):
    model = Class.students.through
    extra = 0
    readonly_fields = ('class',)
    can_delete = False

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ('last_name', 'first_name', 'abbreviation')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = ('class_name', 'grade_level')
    search_fields = ('last_name', 'first_name', 'id')
    inlines = [
        ClassInline,
    ]

@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    search_fields = ('last_name', 'first_name')

@admin.register(Father)
class FatherAdmin(admin.ModelAdmin):
    search_fields = ('last_name', 'first_name')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'iserv_group_name')
    search_fields = ('name',)
