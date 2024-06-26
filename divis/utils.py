from operator import length_hint
import os, csv
from django.conf import settings
from django.http import JsonResponse
import json

from .models import Teacher, Student, Class
from .serializers import TeacherSerializer, StudentSerializer, ClassSerializer

def process_divis_teacher_csv(file_name):
    try:
        return_teachers = [] # Hier wird die Liste der neuen Lehrer gespeichert, die in der CSV-Datei gefunden wurden

        with open(os.path.join(settings.BASE_DIR, file_name), 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Springe zur zweiten Zeile, um die Header-Zeile zu überspringen

            for row in reader:
                first_name, last_name, gender, birth_date, abbreviation = row

                # Speichern des Accounts
                teacher = Teacher.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    birth_date=birth_date,
                    abbreviation=abbreviation
                )
                teacher.save()
                return_teachers.append(teacher)
        
        extracted_teachers = TeacherSerializer(return_teachers, many=True).data

        for teacher in return_teachers:
            teacher.delete()

        return JsonResponse({
            'status': 200,
            'teachers': extracted_teachers, 
        })
    
    except Exception as e:
        print('Error:')
        print(e)
        return JsonResponse({
            'status': 500,
            'error': 'Die Datei scheint nicht das richtige Format zu haben. Bitte überprüfen Sie die Datei und versuchen Sie es erneut.',
            'system_error': str(e)
        })

def extract_teacher_data(line, teachers):
    try:
        teacher_first_name = line.split(';')[0].split(',')[-1].strip()
        teacher_last_name = line.split(';')[0].split(',')[0].split()[-1].strip()
        for i in teachers:
            if i['first_name'] == teacher_first_name and i['last_name'] == teacher_last_name:
                return i['id'], i['abbreviation']
    except Exception as e:
        print(f"Error extracting teacher data: {e}")
    return None, None

def process_and_save_class(classdata, teachers, iserv_accounts):
    if len(classdata) <= 2:
        return None, None

    teacher1 = teacher2 = None
    teacher_abbr1 = teacher_abbr2 = None
    teacher_error_message = None

    # Überprüfen, ob die erste und/oder zweite Zeile Lehrerdaten enthalten
    teacher_line_count = 0
    if "Herr" in classdata[0] or "Frau" in classdata[0]:
        teacher1, teacher_abbr1 = extract_teacher_data(classdata[0], teachers)
        teacher_line_count = 1
        if "Herr" in classdata[1] or "Frau" in classdata[1]:
            teacher2, teacher_abbr2 = extract_teacher_data(classdata[1], teachers)
            teacher_line_count = 2

    # Fehlerbehandlung, wenn kein Lehrer gefunden wurde
    if teacher1 is None and teacher2 is None:
        teacher_error_message = f"{classdata[:2]}"
        teacher_line_count = 1

    # Extrahiere Kursnamen
    classname_line = classdata[teacher_line_count]
    classname = classname_line.split(';')[0]

    # Extrahiere die Schülerdaten ab der entsprechenden Zeile
    class_students = []
    class_student_data = '\n'.join(classdata[teacher_line_count + 2:])

    # Teile die Schülerdaten anhand des Semikolons und lese sie als CSV
    reader = csv.reader(class_student_data.splitlines(), delimiter=';')
    next(reader)  # Überspringe die Header-Zeile
    for row in reader:
        if len(row) >= 10:  # Überprüfe, ob die Zeile genügend Werte hat
            nr, nachname, vorname, geschlecht, geburtsdatum, klassenname, klassenstufe, telefon, strasse, plz, ort, eduport_email, vorname_mutter, nachname_mutter, email_mutter, vorname_vater, nachname_vater, email_vater = row
            if not Student.objects.filter(last_name=nachname, first_name=vorname, birth_date=geburtsdatum).exists():
                iserv_account = ''
                for i in iserv_accounts:
                    if i['first_name'] == vorname and i['last_name'] == nachname:
                        iserv_account = str(i['id'])
                student = Student.objects.create(
                    iserv_account=iserv_account,
                    last_name=nachname,
                    first_name=vorname,
                    gender=geschlecht,
                    birth_date=geburtsdatum,
                    class_name=klassenname,
                    grade_level=klassenstufe,
                    phone=telefon,
                    street=strasse,
                    zip_code=plz,
                    city=ort,
                    eduport_mail=eduport_email
                )
                class_students.append(student)
            else:
                # Füge Schüler aus Datenbank der Liste der Schüler hinzu
                student = Student.objects.get(last_name=nachname, first_name=vorname, birth_date=geburtsdatum)
                class_students.append(student)
        else:
            # Error handling wenn die Zeile nicht genügend Werte hat
            print("ERROR: Row doesn't have enough values")
            print("Skipping row:", row)

    schoolyear_prefix = "2425"
    # Speichere den Kurs
    if teacher1 is None and teacher2 is None:
        new_class = Class.objects.create(
            name=classname,
            teacher_error_message=teacher_error_message
        )
    else:
        teacher_ids = [teacher1] if teacher2 is None else [teacher1, teacher2]
        teacher_abbrs = [abbr for abbr in [teacher_abbr1, teacher_abbr2] if abbr is not None]
        iserv_group_name = 'j' + schoolyear_prefix + '.' + '.'.join(abbr.lower() for abbr in teacher_abbrs) + '.' + classname.replace(' ', '.').lower()
        new_class = Class.objects.create(
            name=classname,
            iserv_group_name=iserv_group_name,
            teacher=teacher_ids,
        )

    # Füge die Schüler dem Kurs hinzu
    new_class.students.set(class_students)
    new_class.save()

    return new_class, class_students

def process_divis_classes_csv(file_name, request_data):
    try:
        return_classes = []  # Liste um die erstellten Kurse zu speichern
        return_students = []  # Liste um die erstellten Schüler zu speichern

        with open(os.path.join(settings.BASE_DIR, file_name), 'r', encoding='utf-8') as file:
            kursdaten = []  # Liste um die Daten jedes Kurses zu speichern
            
            for line in file:
                # Trenne die Zeilen anhand des Zeilenumbruchs
                line = line.strip()
                # Überprüfe ob es sich um eine leere Zeile handelt
                if line == ';;;;;;;;;;;;;;;;;':
                    # Wenn kursdaten nicht leer ist, verarbeite und speichere die Kursdaten
                    if kursdaten:
                        new_class, class_students = process_and_save_class(kursdaten, json.loads(request_data['teachers']), json.loads(request_data['iserv_accounts']))
                        if new_class and class_students is not None: 
                            return_classes.append(new_class)
                            return_students.extend(class_students)
                        # Leere kursdaten
                        kursdaten = []
                else:
                    # Wenn die Zeile nicht nur aus ;;;;;;;;;;;;;;;;; besteht, füge sie zu den aktuellen kursdaten hinzu
                    kursdaten.append(line)

        extracted_classes = ClassSerializer(return_classes, many=True).data
        extracted_students = StudentSerializer(set(return_students), many=True).data

        for _class in return_classes:
            _class.delete()
        
        for student in return_students:
            student.delete()

        return JsonResponse({
            'status': 200,
            'extracted_classes': extracted_classes,
            'extracted_students': extracted_students,
        })

    except Exception as e:
        return JsonResponse({
            'status': 500,
            'error': 'Die Datei scheint nicht das richtige Format zu haben. Bitte überprüfen Sie die Datei und versuchen Sie es erneut.',
            'system_error': str(e)
        })