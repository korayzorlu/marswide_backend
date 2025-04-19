from django.http import JsonResponse

def is_valid_partner_data(data):
    if not data.get('name') or not data.get('formalName'):
        return False, JsonResponse({'message': 'Fill required fields.','status':'error'}, status=400)
    if not data.get('customer') and not data.get('supplier'):
        return False, JsonResponse({'message': 'You must select at least one option, either Customer or Supplier!','status':'error'}, status=400)
    return True, None

def get_partner_types(data):
    types = []
    if data.get('customer'):
        types.append("customer")
    if data.get('supplier'):
        types.append("supplier")
    return types