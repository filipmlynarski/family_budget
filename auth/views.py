from django.contrib.auth.models import User
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'id')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user


class CreateUserView(generics.CreateAPIView):
    model = User
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer
