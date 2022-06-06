import django
import os
import pytest
from django.contrib.auth.models import User
from django.test import TestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from budget.models import Budget, Category


@pytest.mark.django_db
class TestBudget(APITestCase):
    fixtures = ['budget/budget.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        url = reverse('login')
        self.client.post(url, {'username': 'user_1', 'password': 'passwd_1'}, format='json')
        self.token = Token.objects.get(user=self.user)

    def get(self, *args, token=None, **kwargs):
        if token is None:
            token = self.token

        return self.client.get(
            *args,
            **kwargs,
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )

    def post(self, *args, token=None, **kwargs):
        if token is None:
            token = self.token

        return self.client.post(
            *args,
            **kwargs,
            HTTP_AUTHORIZATION=f'Token {token.key}',
            format='json',
        )

    def test_create_user(self):
        url = reverse('register')
        data = {'username': 'user_3', 'password': 'password_3'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(User.objects.filter(username=data['username']).exists())

    def test_login_user(self):
        url = reverse('register')
        data = {'username': 'user_3', 'password': 'password_3'}
        self.client.post(url, data, format='json')

        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(Token.objects.filter(user=self.user).exists())

    def test_login_invalid_user(self):
        url = reverse('login')
        data = {'username': 'user_1', 'password': 'invalid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category(self):
        url = reverse('categories')
        data = {'name': 'category_2'}
        response = self.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.filter(name=data['name']).count(), 1)

    def test_list_categories(self):
        url = reverse('categories')
        data = {'name': 'category_2'}
        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('categories')
        response = self.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            'count': 2, 'next': None, 'previous': None,
            'results': [{'id': 1, 'name': 'category_1', 'owner': 1, 'users': []},
                        {'id': 4, 'name': 'category_2', 'owner': 1, 'users': []}]
        }
        self.assertDictEqual(response.json(), expected)
        self.assertEqual(Category.objects.all().count(), 2)

    def test_get_category_details(self):
        url = reverse('category', kwargs={'pk': 1})
        response = self.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {'id': 1, 'name': 'category_1', 'owner': 1, 'users': []}
        self.assertDictEqual(response.json(), expected)

    def test_add_user_to_category(self):
        user = User.objects.get(id=2)
        url = reverse('add_to_category', kwargs={'category_pk': 1, 'user_pk': user.id})
        response = self.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {'id': 1, 'name': 'category_1', 'users': [2]}
        self.assertDictEqual(response.json(), expected)

    def test_add_budget(self):
        url = reverse('budget', kwargs={'category_pk': 1})
        data = {'type': Budget.Type.INCOME.value, 'amount': 100}
        response = self.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = {'user': 1, 'type': 'IN', 'amount': '100.00', 'category': 1}
        self.assertDictEqual(response.json(), expected)

    def test_get_category_with_budgets(self):
        user_1 = User.objects.get(id=1)
        user_2 = User.objects.get(id=2)

        url = reverse('login')
        self.client.post(url, {'username': 'user_2', 'password': 'passwd_1'}, format='json')
        token_2 = Token.objects.get(user=user_2)

        category_1 = Category.objects.get(pk=1)
        category_1.users.add(user_2)
        category_1.save()

        category_2 = Category.objects.create(owner=user_2, name='category_2')

        budgets = [
            Budget(type=Budget.Type.INCOME.value, amount=100, category=category_1, user=user_1),
            Budget(type=Budget.Type.EXPENSE.value, amount=40, category=category_1, user=user_2),
            Budget(type=Budget.Type.INCOME.value, amount=1_000, category=category_2, user=user_2),
        ]
        Budget.objects.bulk_create(budgets)

        url = reverse('budget', kwargs={'category_pk': 1})
        response = self.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [{'user': 1, 'type': 'EX', 'amount': '100.00', 'category': 1},
                    {'user': 2, 'type': 'IN', 'amount': '300.00', 'category': 1},
                    {'user': 1, 'type': 'IN', 'amount': '100.00', 'category': 1},
                    {'user': 2, 'type': 'EX', 'amount': '40.00', 'category': 1}]
        self.assertListEqual(response.json(), expected)

        response = self.get(url, token=token_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

        # second category that only user_2 has access to
        url = reverse('budget', kwargs={'category_pk': category_2.id})
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.get(url, token=token_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [{'user': 2, 'type': 'IN', 'amount': '1000.00', 'category': 3}]
        self.assertListEqual(response.json(), expected)
