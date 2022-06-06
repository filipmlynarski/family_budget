from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Budget(models.Model):
    class Type(models.TextChoices):
        INCOME = 'IN', _('Income')
        EXPENSE = 'EX', _('Expense')

    type = models.CharField(max_length=2, choices=Type.choices)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    users = models.ManyToManyField(User, related_name='budgets')
