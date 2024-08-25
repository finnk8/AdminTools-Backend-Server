import csv, os
from django.conf import settings
from django.http import JsonResponse
from difflib import SequenceMatcher

from iserv.serializers import ExistingAccountSerializer, IservGroupSerializer
from .models import IservGroup, ExistingAccount


def process_iserv_exported_users_csv(file_name):
    try:
        return_accounts = [] # Hier wird die Liste der neuen Accounts gespeichert, die in der CSV-Datei gefunden wurden
        return_groups = [] # Hier wird die Liste der neuen Gruppen gespeichert, die in der CSV-Datei gefunden wurden

        with open(os.path.join(settings.BASE_DIR, file_name), 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Springe zur zweiten Zeile, um die Header-Zeile zu überspringen
            
            row_index = 2
            for row in reader:
                print(row_index)
                row_index += 1
                account, first_name, last_name, status, created_at, created_by, internal_id, user_type, import_id, class_information, email, groups_str = row
                gruppen_data = groups_str.split(',')
                
                # Speichern der Gruppen
                gruppen_objs = []
                for gruppe_str in gruppen_data:
                    if gruppe_str == '':
                        continue
                    gruppe, _ = IservGroup.objects.get_or_create(group_name=gruppe_str)
                    gruppen_objs.append(gruppe)
                    return_groups.append(gruppe)
                
                # Speichern des Accounts, falls er nicht existiert
                account = ExistingAccount.objects.create(
                    account=account,
                    first_name=first_name,
                    last_name=last_name,
                    status=status,
                    created_at=created_at,
                    created_by=created_by,
                    internal_id=internal_id,
                    user_type=user_type,
                    import_id=import_id,
                    class_information=class_information,
                    email=email
                )
                account.groups.set(gruppen_objs)
                account.save()
                return_accounts.append(account)

        
        extracted_accounts = ExistingAccountSerializer(return_accounts, many=True).data
        extracted_groups = IservGroupSerializer(list(dict.fromkeys(return_groups)), many=True).data

        # Clean up accounts, so no data is left behind
        for account in return_accounts:
            for group in account.groups.all():
                try:
                    IservGroup.objects.get(group_name=group).delete()
                except:
                    pass
            account.delete()
        
        return JsonResponse({
            'status': 200,
            'accounts': extracted_accounts,
            'iserv_groups': extracted_groups
        })
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'error': 'Die Datei scheint nicht das richtige Format zu haben. Bitte überprüfen Sie die Datei und versuchen Sie es erneut.'
        })
    
def process_iserv_accounts_for_duplicates(request_data):
    try:
        # Liste von Accountnamen
        accounts = request_data['accounts']
        accounts_to_check = []

        # Funktion zur Berechnung der Ähnlichkeit zwischen zwei Strings
        def similarity(a, b):
            return SequenceMatcher(None, a, b).ratio()

        # Funktion zur Ermittlung der ähnlichsten Accounts für einen gegebenen Account
        def find_similar_accounts(query, threshold=0.9):
            similar_accounts = []
            for account in accounts:
                sim_score = similarity(query, account['account'])
                if sim_score >= threshold and query != account['account']:
                    similar_accounts.append((account['id'], sim_score))
            return similar_accounts

        # Beispiel: Suche nach ähnlichen Accounts für den Account "aarnavi.aalina.soni"
        for i in accounts:
            query_account = i['account']
            similar_accounts = find_similar_accounts(query_account)
            if similar_accounts:
                accounts_to_check.append({
                    'account': i['id'],
                    'similar_accounts': similar_accounts
                })
        
        return JsonResponse({
            'status': 200,
            'message': 'Die Suche nach ähnlichen Accounts wurde erfolgreich abgeschlossen.',
            'accounts_to_check': accounts_to_check
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'error': 'Die Suche nach ähnlichen Accounts konnte nicht abgeschlossen werden. Bitte versuchen Sie es erneut.',
            'system_error': str(e)
        })