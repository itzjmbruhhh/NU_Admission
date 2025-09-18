"""
URL configuration for admission_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from admissions.views import index, loginAdmin, adminDash, register_student, student_detail

urlpatterns = [
    path('super_admin/', admin.site.urls),
    path('loginAdmin/', loginAdmin, name='loginAdmin'),
    path('adminDash/', adminDash, name='landingAdmin'),
    # Registration endpoint handles GET (form) and POST (save) via register_student
    path('register/', register_student, name='register'),
    path('student/<int:pk>/', student_detail, name='student_detail'),
    path('', index, name='index')

]
