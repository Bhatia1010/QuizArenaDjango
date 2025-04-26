from django.db import models

class Topic(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('article', 'Article'),
        ('video', 'Video'),
        ('code', 'Code Example'),
        ('exercise', 'Exercise'),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title