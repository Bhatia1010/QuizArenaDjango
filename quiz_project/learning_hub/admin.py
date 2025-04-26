from django.contrib import admin
from .models import Topic, Resource

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    ordering = ('order',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'resource_type', 'order', 'created_at')
    list_filter = ('resource_type', 'topic')
    search_fields = ('title', 'description', 'content')
    ordering = ('topic', 'order')