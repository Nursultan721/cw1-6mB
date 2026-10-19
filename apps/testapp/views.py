from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import google_auth_service

class GoogleAuthView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Code field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = google_auth_service(code)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)