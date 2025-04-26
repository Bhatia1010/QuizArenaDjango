"""
URL configuration for quiz_project project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from quiz_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz_app.urls')),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('staff/quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('staff/quiz/<int:quiz_id>/review/', views.review_answers, name='review_answers'),
    path('staff/attempt/<int:attempt_id>/view/', views.view_attempt, name='view_attempt'),
    path('staff/attempt/<int:attempt_id>/delete/', views.delete_attempt, name='delete_attempt'),
    path('staff/create-quiz/', views.create_quiz_staff, name='create_quiz_staff'),
    path('staff/create-default-quizzes/', views.create_default_quizzes, name='create_default_quizzes'),
    path('admin/', admin.site.urls),
    path('', include('quiz_app.urls')),
    path('learning/', include('learning_hub.urls')),  # Add this line
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)