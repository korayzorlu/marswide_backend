from django.http import JsonResponse

def is_valid_account_data(data):
    if not data.get('partner') or not data.get('currency'):
        return False, JsonResponse({'message': 'Fill required fields.','status':'error'}, status=400)
    
    return True, None