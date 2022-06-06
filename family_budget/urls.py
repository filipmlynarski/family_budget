"""family_budget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.authtoken import views

import auth.views
import budget.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', auth.views.CreateUserView.as_view()),
    path('accounts/login/', views.obtain_auth_token),
    path('accounts/logout/', auth_views.LogoutView.as_view()),
    path('budget/categories/', budget.views.CategoriesView.as_view()),
    path('budget/categories/<int:pk>', budget.views.CategoryDetail.as_view()),
    path('budget/budgets/', budget.views.BudgetView.as_view()),
]
