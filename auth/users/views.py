from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSeriaLizer
from rest_framework.response import Response
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSeriaLizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Пользователь не найден')

        payload = {
            'id' : user.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        responce = Response()
        responce.set_cookie(key='jwt', value=token, httponly=True)
        responce.data={
            'jwt': token
        }

        return responce

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed(" Не прошедший проверку пользователь")
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Не прошел проверку подлинности')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSeriaLizer(user)
        return Response(serializer.data)

class Logout(APIView):
    def post(self,request):
        responce = Response()
        responce.delete_cookie('jwt')
        responce.data = {
            'message': 'Успешно'
        }

        return responce

