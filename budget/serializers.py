from django.contrib.auth.models import User
from rest_framework import serializers

from budget.models import Budget, Category


class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Category
        fields = ('id', 'name', 'owner', 'users')
        read_only_fields = ('users',)


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'users')


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('user', 'type', 'amount', 'category')
