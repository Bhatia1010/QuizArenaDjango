from django.urls import path
from . import views

app_name = 'learning_hub'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('topic/<int:topic_id>/submit/', views.submit_resource, name='submit_resource'),
    path('topic/<int:topic_id>/resource/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
]