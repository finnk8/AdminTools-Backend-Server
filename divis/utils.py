from operator import length_hint
import os, csv
from django.conf import settings
from django.http import JsonResponse
import json

from .models import Teacher, Student, Class, Mother, Father
from .serializers import TeacherSerializer, StudentSerializer, ClassSerializer, MotherSerializer, FatherSerializer

def process_divis_teacher_csv(file_name, request_data):
    try:
        iserv_accounts = json.loads(request_data['iserv_accounts'])
        return_teachers = [] # Hier wird die Liste der neuen Lehrer gespeichert, die in der CSV-Datei gefunden wurden

        with open(os.path.join(settings.BASE_DIR, file_name), 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Springe zur zweiten Zeile, um die Header-Zeile zu überspringen

            for row in reader:
                try:
                    first_name, last_name, gender, birth_date, abbreviation = row

                    iserv_account_id = None
                    for i in iserv_accounts:
                        if i['first_name'] == first_name and i['last_name'] == last_name:
                            iserv_account_id = i['id']

                    
                    # Speichern des Accounts
                    teacher = Teacher.objects.create(
                        iserv_account=iserv_account_id,
                        first_name=first_name,
                        last_name=last_name,
                        gender=gender,
                        birth_date=birth_date,
                        abbreviation=abbreviation
                    )
                    teacher.save()
                    return_teachers.append(teacher)
                except Exception as e:
                    print('Error:')
                    print(e)
                    print('Row:')
                    print(row)
        
        extracted_teachers = TeacherSerializer(return_teachers, many=True).data

        for teacher in return_teachers:
            teacher.delete()

        return JsonResponse({
            'status': 200,
            'teachers': extracted_teachers, 
        })
    
    except Exception as e:
        for teacher in return_teachers:
            teacher.delete()
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
        print('Error:')
        print(e)
    return None, None

def process_and_save_class(classdata, teachers, iserv_accounts, schoolyear_prefix):
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
        try:
            while i in classdata != 'Nr.;Nachname;Vorname;m/w;Geburtsdatum;Klassenname;Klassenstufe;Telefon;Straße;PLZ;Ort;eduPort-Mailadresse;Vorname (Mutter);Nachname (Mutter);E-Mail (Mutter);Vorname (Vater);Nachname (Vater);E-Mail (Vater)':
                teacher_error_message += i
        except Exception as e:
            teacher_error_message = classdata[0:2]
    # Extrahiere Kursnamen
    classname_line = classdata[teacher_line_count]
    classname = classname_line.split(';')[0]

    # Extrahiere die Schülerdaten ab der entsprechenden Zeile
    if teacher_line_count + 2 >= len(classdata):
        return None, None
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
                        iserv_account = i['id']
                student = Student.objects.create(
                    iserv_account=iserv_account if iserv_account != '' else None,
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
                if vorname_mutter != '' and nachname_mutter != '':
                    if Mother.objects.filter(first_name=vorname_mutter, last_name=nachname_mutter, email=email_mutter).exists():
                        mother = Mother.objects.get(first_name=vorname_mutter, last_name=nachname_mutter, email=email_mutter)
                        new_child_array = json.loads(mother.child)
                        new_child_array.append(student.id)
                        mother.child = json.dumps(new_child_array)
                        mother.save()
                    else:
                        mother = Mother.objects.create(
                            first_name=vorname_mutter,
                            last_name=nachname_mutter,
                            email=email_mutter,
                            child = json.dumps([student.id])
                        )
                if vorname_vater != '' and nachname_vater != '':
                    if Father.objects.filter(first_name=vorname_vater, last_name=nachname_vater, email=email_vater).exists():
                        father = Father.objects.get(first_name=vorname_vater, last_name=nachname_vater, email=email_vater)
                        new_child_array = json.loads(father.child)
                        new_child_array.append(student.id)
                        father.child = json.dumps(new_child_array)
                        father.save()
                    else:
                        father = Father.objects.create(
                            first_name=vorname_vater,
                            last_name=nachname_vater,
                            email=email_vater,
                            child = json.dumps([student.id])
                        )
            else:
                # Füge Schüler aus Datenbank der Liste der Schüler hinzu
                student = Student.objects.get(last_name=nachname, first_name=vorname, birth_date=geburtsdatum)
                class_students.append(student)
        else:
            # Error handling wenn die Zeile nicht genügend Werte hat
            print("ERROR: Row doesn't have enough values")
            print("Skipping row:")

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
                        new_class, class_students = process_and_save_class(kursdaten, json.loads(request_data['teachers']), json.loads(request_data['iserv_accounts']), json.loads(request_data['settings']).get('schoolyearPrefix'))
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
        extracted_mothers = MotherSerializer(Mother.objects.all(), many=True).data
        extracted_fathers = FatherSerializer(Father.objects.all(), many=True).data

        for _class in return_classes:
            _class.delete()
        
        for student in return_students:
            student.delete()
            
        for mother in Mother.objects.all():
            mother.delete()
        
        for father in Father.objects.all():
            father.delete()
        
        return JsonResponse({
            'status': 200,
            'extracted_classes': extracted_classes,
            'extracted_students': extracted_students,
            'extracted_mothers': extracted_mothers,
            'extracted_fathers': extracted_fathers
        })

    except Exception as e:
        # print('------')
        # print('Error in process_divis_classes_csv:')
        # print('Error: ' + str(e))
        # print('Daten: ' + str(kursdaten))
        # print('------')
        for _class in return_classes:
            _class.delete()
        
        for student in return_students:
            student.delete()
            
        for mother in Mother.objects.all():
            mother.delete()
        
        for father in Father.objects.all():
            father.delete()
        return JsonResponse({
            'status': 500,
            'error': 'Die Datei scheint nicht das richtige Format zu haben. Bitte überprüfen Sie die Datei und versuchen Sie es erneut.',
            'system_error': str(e)
        })