# services.py
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def google_auth_service(code):
    # Шаг 1. Обмен code на access_token от Google
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": getattr(settings, "GOOGLE_CLIENT_ID", ""),
        "client_secret": getattr(settings, "GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": "postmessage", # или ваш фронтенд URI
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data=payload)
    token_data = response.json()
    
    if "access_token" not in token_data:
        raise ValueError("Invalid Google authorization code")
        
    google_access_token = token_data["access_token"]

    # Шаг 2. Запрос профиля пользователя
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {google_access_token}"}
    userinfo_response = requests.get(userinfo_url, headers=headers)
    user_data = userinfo_response.json()

    email = user_data.get("email")
    if not email:
        raise ValueError("Email could not be retrieved from Google")

    # Шаг 3. Поиск или создание пользователя (по умолчанию роль 'student')
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "role": "student"
        }
    )

    # Шаг 4. Генерация SimpleJWT токенов
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "is_new_user": created,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }