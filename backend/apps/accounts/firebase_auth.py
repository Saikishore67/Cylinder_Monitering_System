import firebase_admin.auth as firebase_auth
from django.http import JsonResponse

def verify_firebase_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None, JsonResponse({'error': 'No token provided'}, status=401)
    
    token = auth_header.split(' ')[1]

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token, None
    except firebase_auth.ExpiredIdTokenError:
        return None, JsonResponse({'error': 'Token expired'}, status=401)
    except firebase_auth.InvalidIdTokenError:
        return None, JsonResponse({'error': 'Invalid token'}, status=401)
    except Exception as e:
        return None, JsonResponse({'error': str(e)}, status=401)