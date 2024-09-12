import csv, json
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@api_view(['POST'])
@csrf_exempt
def download_iserv_import(request):
    if request.method == 'POST':
        return generate_csv_iserv_student_import(request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')

@api_view(['POST'])
@csrf_exempt
def download_iserv_import_parents(request):
    if request.method == 'POST':
        return generate_csv_iserv_parents_import(request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')


def generate_csv_iserv_student_import(data):
    # Query the database to retrieve data
    students = json.loads(data['students'])
    classes = json.loads(data['classes'])
    try:
        iserv_accounts = json.loads(data['iserv_accounts'])
    except:
        iserv_accounts = []
    schoolyear_prefix = json.loads(data['settings']).get('schoolyearPrefix')

    # Define the headers for your CSV file
    headers = ['Import ID', 'Vorname', 'Nachname', 'Klasse', 'Gruppen']

    # Generate file name with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f'admintools_export_{timestamp}.csv'

    # Write data to CSV file
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        
        # Write headers
        writer.writerow(headers)
        
        # Write rows
        for student in students:
            student_iserv_id = student.get('iserv_account', '')
            if student_iserv_id:
                iserv_account = None
                for account in iserv_accounts:
                    if account.get('id') == student_iserv_id:
                        iserv_account = account
                        break
            else:
                iserv_account = None
            try:
                if student['classes'] != '':
                    group_names = []
                    if student['class_name']:
                        group_names.append(str('j'+schoolyear_prefix+'.'+student['class_name'].replace(' ', '').replace('/','').lower())) 
                    for _class in student['classes']:
                        group_names.append(next((item for item in classes if item["id"] == _class['id']), None)['iserv_group_name'])
                    csv_classes = ';'.join([str(cls) for cls in group_names])
            except:
                csv_classes = ''
                            
            row = [
                iserv_account['import_id'] if iserv_account else '',
                student['first_name'] if student['first_name'] else '',
                student['last_name'] if student['last_name'] else '',
                student['class_name'] if student['class_name'] else '',
                csv_classes if csv_classes else ''
            ]
            writer.writerow(row)
    
    # Serve the CSV file as an HTTP response
    with open(file_name, 'rb') as csv_file:
        response = HttpResponse(csv_file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

def generate_csv_iserv_parents_import(data):
    # Query the database to retrieve data
    students = json.loads(data['students'])
    iserv_accounts = json.loads(data['iserv_accounts'])
    mothers = json.loads(data['mothers'])
    fathers = json.loads(data['fathers'])

    parents = mothers + fathers
    print(type(parents))

    # Define the headers for your CSV file
    headers = ['Vorname', 'Nachname', 'Email', 'Kind-ID']

    # Generate file name with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f'admintools_export_{timestamp}.csv'

    # Write data to CSV file
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        
        # Write headers
        writer.writerow(headers)
        
        # Write rows
        for parent in parents:
            try:
                for child in json.loads(parent['child']):
                    student = next((item for item in students if item["id"] == child), None)
                    iserv_account = next((item for item in iserv_accounts if item["id"] == student['iserv_account']), None)
                    if student and iserv_account['import_id']:
                        row = [
                            parent['first_name'] if parent['first_name'] else '',
                            parent['last_name'] if parent['last_name'] else '',
                            parent['email'] if parent['email'] else '',
                            iserv_account['import_id'] if iserv_account else ''
                        ]
                        writer.writerow(row)
            except:
                pass
    
    # Serve the CSV file as an HTTP response
    with open(file_name, 'rb') as csv_file:
        response = HttpResponse(csv_file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response