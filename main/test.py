import csv, json
from datetime import datetime
from django.http import HttpResponse
from divis.models import Student
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@api_view(['POST'])
@csrf_exempt
def download_iserv_import(request):
    if request.method == 'POST':
        return generate_csv_from_database_data(request.data)
    else:
        return HttpResponse(status=405, content='Method Not Allowed')


def generate_csv_from_database_data(data):
    # Query the database to retrieve data
    students = json.loads(data['students'])
    classes = json.loads(data['classes'])
    iserv_accounts = json.loads(data['iserv_accounts'])

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