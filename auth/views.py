from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny

from auth.serializers import CreateUserSerializer


class CreateUserView(generics.CreateAPIView):
    model = User
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer
