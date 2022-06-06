from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class CategoriesView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'users')


class AddToCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, category_pk, user_pk):
        category = get_object_or_404(
            Category.objects.filter(owner=request.user),
            pk=category_pk,
        )
        user = get_object_or_404(User.objects.exclude(pk=request.user.id), pk=user_pk)

        category.users.add(user)
        category.save()

        return Response(CategoryDetailSerializer(instance=category).data, status=status.HTTP_200_OK)


class CategoryDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('user', 'type', 'amount', 'category')


class BudgetView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, category_pk):
        category = get_object_or_404(
            Category.objects.filter(Q(owner=request.user) | Q(users=request.user)),
            pk=category_pk,
        )

        serializer = BudgetSerializer(instance=category.budget_set.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, category_pk):
        category = get_object_or_404(
            Category.objects.filter(Q(owner=request.user) | Q(users=request.user)),
            pk=category_pk,
        )

        data = {
            'user': request.user.id,
            'category': category.id,
        }
        for key, value in request.data.items():
            data[key] = value if not isinstance(value, list) else value[0]

        serializer = BudgetSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
