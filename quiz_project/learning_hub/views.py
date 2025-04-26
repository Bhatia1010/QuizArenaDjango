from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Topic, Resource
from .forms import ResourceSubmissionForm

def is_staff_user(user):
    return user.is_staff or user.is_superuser

def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'learning_hub/topic_list.html', {'topics': topics})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    resources = topic.resources.all()
    
    # Handle resource submission
    if request.method == 'POST':
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("You don't have permission to submit resources.")
        
        form = ResourceSubmissionForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.topic = topic
            resource.save()
            messages.success(request, 'Resource submitted successfully!')
            return redirect('learning_hub:topic_detail', topic_id=topic_id)
    else:
        form = ResourceSubmissionForm()
    
    return render(request, 'learning_hub/topic_detail.html', {
        'topic': topic,
        'resources': resources,
        'form': form
    })

def resource_detail(request, topic_id, resource_id):
    topic = get_object_or_404(Topic, id=topic_id)
    resource = get_object_or_404(Resource, id=resource_id, topic=topic)
    return render(request, 'learning_hub/resource_detail.html', {
        'topic': topic,
        'resource': resource
    })

@login_required
@user_passes_test(is_staff_user)  # This decorator ensures only staff users can submit resources
def submit_resource(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        form = ResourceSubmissionForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.topic = topic
            resource.save()
            messages.success(request, 'Resource submitted successfully!')
            return redirect('learning_hub:topic_detail', topic_id=topic_id)
    else:
        form = ResourceSubmissionForm()
    
    return render(request, 'learning_hub/submit_resource.html', {
        'topic': topic,
        'form': form
    })

@login_required
@user_passes_test(is_staff_user) # This decorator ensures only staff users can edit resources
def edit_resource(request, topic_id, resource_id):
    topic = get_object_or_404(Topic, id=topic_id)
    resource = get_object_or_404(Resource, id=resource_id, topic=topic)
    
    if request.method == 'POST':
        form = ResourceSubmissionForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('learning_hub:resource_detail', topic_id=topic_id, resource_id=resource_id)
    else:
        form = ResourceSubmissionForm(instance=resource)
    
    return render(request, 'learning_hub/edit_resource.html', {
        'topic': topic,
        'resource': resource,
        'form': form
    })