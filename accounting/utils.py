from django.http import JsonResponse

def is_valid_account_data(data):
    if not data.get('partner') or not data.get('currency'):
        return False, JsonResponse({'message': 'Fill required fields.','status':'error'}, status=400)
    
    return True, None

def is_valid_invoice_data(data):
    if not data.get('partner') or not data.get('currency') or not data.get('invoice_no') or not data.get('amount'):
        return False, JsonResponse({'message': 'Fill required fields.','status':'error'}, status=400)
    
    return True, None

def is_valid_payment_data(data):
    if not data.get('partner') or not data.get('currency') or not data.get('amount'):
        return False, JsonResponse({'message': 'Fill required fields.','status':'error'}, status=400)
    
    return True, None