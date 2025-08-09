import os
import math
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from .models import Task, CustomUser, Profile, Education, Document, SocialLink, StudyMaterial, Application, Notification,MaterialView
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Sum, Count, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control

#----------------------------------------------------------------
logger = logging.getLogger(__name__)
User = get_user_model() 
# -------------------- Basic Views --------------------

def home(request):
    """Home page view."""
    return render(request, 'shop/index.html')

@login_required
def about(request):
    """About page view."""
    return render(request, 'shop/about.html')
@login_required
def base(request):
    """Base page view with tasks data."""
    try:
        # Fetch all tasks with related user data
        tasks = Task.objects.select_related('created_by').all()
        recent_tasks = Task.objects.select_related('created_by').order_by('-id')[:5]
        context = {
            'tasks': tasks,
            'recent_tasks': recent_tasks,

        }
    except Exception as e:
        # Log the error in production
        messages.error(request, "Error loading tasks data.")
        context = {
            'tasks': [],
            'recent_tasks': [],
        }
    
    return render(request, 'shop/base.html', context)

#-----------------------------------------
@login_required
def study_material(request):
    try:
        # Fetch all study materials with related user data
        study_materials = StudyMaterial.objects.select_related('user').all()
        recent_study_materials = StudyMaterial.objects.select_related('user').order_by('-id')[:5]
        context = {
            'study_materials': study_materials,
            'recent_study_materials': recent_study_materials,
        }
        return render(request, 'shop/study_material.html', context)
    except Exception as e:
        # Log the error in production
        messages.error(request, "Error loading study materials data.")
        context = {
            'study_materials': [],
            'recent_study_materials': [],
        }
        return render(request, 'shop/study_material.html', context)
#------------------------------------------------------------------ 
@login_required
def join(request):
    """Join page view."""
    return render(request, 'shop/join.html')
@login_required
def post(request):
    """Post page view."""
    return render(request, 'shop/post.html')
@login_required
def settings(request):
    return render(request, 'shop/account_settings.html')


def logout_page(request):
    """User logout view."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully!")
    
    return redirect('home')


@receiver(user_logged_in)
def redirect_to_otp_setup(sender, request, user, **kwargs):
    """Redirect to OTP setup if not configured"""
    from django_otp.plugins.otp_email.models import EmailDevice
    
    if not EmailDevice.objects.filter(user=user, confirmed=True).exists():
        # Redirect to OTP setup
        pass


# -------------------- Profile Views --------------------

@login_required
def profile(request):
    """User profile view - requires authentication."""
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get user's social accounts
    social_accounts = []
    if hasattr(request.user, 'socialaccount_set'):
        social_accounts = request.user.socialaccount_set.all()
    
    context = {
        'user': request.user,
        'profile': profile,
        'educations': request.user.educations.all(),
        'documents': request.user.documents.all(),
        'social_links': request.user.social_links.all(),
        'social_accounts': social_accounts,
        'is_owner': True,
    }
    return render(request, 'shop/profile.html', context)


@login_required
def profile_view(request, pk=None):
    """Display user profile by ID"""
    if pk:
        user = get_object_or_404(User, pk=pk)
    else:
        user = request.user
    
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Increment view count if it's not the owner viewing their own profile
    if request.user.is_authenticated and request.user != user:
        profile.views += 1
        profile.save()
    
    context = {
        'user': user,
        'profile': profile,
        'educations': user.educations.all(),
        'documents': user.documents.filter(is_public=True),
        'social_links': user.social_links.filter(is_public=True),
        'is_owner': request.user == user if request.user.is_authenticated else False,
    }
    
    return render(request, 'profile.html', context)


def public_profile_view(request, username):
    """Public profile view with session-based one view per user"""
    user = get_object_or_404(CustomUser, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Check if the viewer is not the profile owner
    if request.user.is_authenticated and request.user != user:
        session_key = f'viewed_profile_{user.id}'
        
        if not request.session.get(session_key, False):
            profile.views += 1
            profile.save()
            request.session[session_key] = True  # Mark as viewed
    
    context = {
        'user': user,
        'profile': profile,
        'educations': user.educations.all(),
        'documents': user.documents.filter(is_public=True),
        'social_links': user.social_links.filter(is_public=True),
        'is_owner': request.user == user if request.user.is_authenticated else False,
    }
    
    return render(request, 'shop/profile.html', context)
#----------------------------------------------------------------
@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # ADD THIS CODE HERE - Handle image deletions FIRST
        if request.POST.get('delete_profile_picture') == 'true':
            if profile.profile_picture:
                profile.profile_picture.delete()
                profile.profile_picture = None

        if request.POST.get('delete_banner_image') == 'true':
            if profile.banner_image:
                profile.banner_image.delete()
                profile.banner_image = None
        
        # Then handle your existing form processing
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        
        # Update profile fields
        profile.location = request.POST.get('location', '')
        profile.phone = request.POST.get('phone', '')
        profile.website = request.POST.get('website', '')
        profile.bio = request.POST.get('bio', '')
        
        # Handle new file uploads (only if not being deleted)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'banner_image' in request.FILES:
            profile.banner_image = request.FILES['banner_image']
            
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('shop/account_settings.html')
    
    # GET request handling...

# -------------------- Profile Management --------------------

@login_required
@require_POST
def edit_profile(request):
    """Handle profile editing"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    try:
        # Update user information
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        # Update profile information
        profile.title = request.POST.get('title', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        profile.phone = request.POST.get('phone', '').strip()
        profile.website = request.POST.get('website', '').strip()
        
        # Handle profile picture upload
        if request.FILES.get('profile_picture'):
            # Delete old profile picture if exists
            if profile.profile_picture:
                default_storage.delete(profile.profile_picture.name)
            profile.profile_picture = request.FILES['profile_picture']
        
        # Handle banner image upload
        if request.FILES.get('banner_image'):
            # Delete old banner image if exists
            if profile.banner_image:
                default_storage.delete(profile.banner_image.name)
            profile.banner_image = request.FILES['banner_image']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        
    except Exception as e:
        messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('profile')


# -------------------- Account Settings --------------------

@login_required
def account_settings(request):
    """Account settings view"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get user's social accounts if django-allauth is being used
    social_accounts = []
    if hasattr(request.user, 'socialaccount_set'):
        social_accounts = request.user.socialaccount_set.all()
    
    context = {
        'user': request.user,
        'profile': profile,
        'social_accounts': social_accounts,
    }
    
    return render(request, 'shop/account_settings.html', context)


@login_required
@require_POST
def increment_profile_views(request):
    """AJAX endpoint to increment profile views"""
    try:
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.views += 1
        profile.save()
        return JsonResponse({'success': True, 'views': profile.views})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# -------------------- Document Management --------------------

@login_required
@require_POST
def upload_document(request):
    """Handle document upload"""
    try:
        title = request.POST.get('title', '').strip()
        document_type = request.POST.get('document_type', '').strip()
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        file = request.FILES.get('file')
        
        if not all([title, document_type, file]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('profile')
        
        # Validate file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size must be less than 10MB.')
            return redirect('profile')
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in allowed_extensions:
            messages.error(request, 'File type not allowed. Please upload PDF, DOC, DOCX, JPG, or PNG files.')
            return redirect('profile')
        
        # Create document
        document = Document.objects.create(
            user=request.user,
            title=title,
            document_type=document_type,
            description=description,
            file=file,
            is_public=is_public
        )
        
        messages.success(request, 'Document uploaded successfully!')
        
    except Exception as e:
        messages.error(request, f'Error uploading document: {str(e)}')
    
    return redirect('profile')


@login_required
@require_POST
def delete_document(request, document_id):
    """Delete a document"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    try:
        # Delete the file from storage
        if document.file:
            default_storage.delete(document.file.name)
        
        # Delete the document record
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting document: {str(e)}')
    
    return redirect('profile')


# -------------------- Social Link Management --------------------

@login_required
@require_POST
def add_social_link(request):
    """Handle social link addition"""
    try:
        platform = request.POST.get('platform', '').strip()
        username = request.POST.get('username', '').strip()
        url = request.POST.get('url', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not all([platform, username, url]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('profile')
        
        # Check if this combination already exists
        if SocialLink.objects.filter(user=request.user, platform=platform, username=username).exists():
            messages.error(request, 'This social link already exists.')
            return redirect('profile')
        
        # Create social link
        social_link = SocialLink.objects.create(
            user=request.user,
            platform=platform,
            username=username,
            url=url,
            is_public=is_public
        )
        
        messages.success(request, 'Social link added successfully!')
        
    except Exception as e:
        messages.error(request, f'Error adding social link: {str(e)}')
    
    return redirect('profile')


@login_required
@require_POST
def delete_social_link(request, link_id):
    """Delete a social link"""
    social_link = get_object_or_404(SocialLink, id=link_id, user=request.user)
    
    try:
        social_link.delete()
        messages.success(request, 'Social link deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting social link: {str(e)}')
    
    return redirect('profile')


# -------------------- Education Management --------------------

@login_required
@require_POST
def add_education(request):
    """Handle education addition"""
    try:
        institution = request.POST.get('institution', '').strip()
        degree = request.POST.get('degree', '').strip()
        field_of_study = request.POST.get('field_of_study', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        currently_studying = request.POST.get('currently_studying') == 'on'
        
        if not all([institution, degree, start_date]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('profile')
        
        # If currently studying, don't save end_date
        if currently_studying:
            end_date = None
        
        # Create education
        education = Education.objects.create(
            user=request.user,
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            start_date=start_date,
            end_date=end_date,
            
        )
        
        messages.success(request, 'Education added successfully!')
        
    except Exception as e:
        messages.error(request, f'Error adding education: {str(e)}')
    
    return redirect('profile')


@login_required
@require_POST
def edit_education(request, education_id):
    """Handle education editing"""
    education = get_object_or_404(Education, id=education_id, user=request.user)
    
    try:
        education.institution = request.POST.get('institution', '').strip()
        education.degree = request.POST.get('degree', '').strip()
        education.field_of_study = request.POST.get('field_of_study', '').strip()
        education.start_date = request.POST.get('start_date')
        education.end_date = request.POST.get('end_date')
        
        currently_studying = request.POST.get('currently_studying') == 'on'
        
        if not all([education.institution, education.degree, education.start_date]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('profile')
        
        # If currently studying, don't save end_date
        if currently_studying:
            education.end_date = None
        
        education.save()
        messages.success(request, 'Education updated successfully!')
        
    except Exception as e:
        messages.error(request, f'Error updating education: {str(e)}')
    
    return redirect('profile')


@login_required
@require_POST
def delete_education(request, education_id):
    """Delete an education entry"""
    education = get_object_or_404(Education, id=education_id, user=request.user)
    
    try:
        education.delete()
        messages.success(request, 'Education entry deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting education: {str(e)}')
    
    return redirect('profile')


#--------------------- URL Patterns --------------------
@login_required
def create_task(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            budget = request.POST.get('budget')
            category = request.POST.get('category')
            deadline = request.POST.get('deadline')
            task_assigned_place = request.POST.get('task_assigned_place')
            is_approved = request.POST.get('is_approved') == 'on'  # Handle checkbox
            
            # Validate required fields
            if not all([title, description, budget, category]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('post')
            
            # Check if user has agreed to approval terms (checkbox must be checked)
            if not is_approved:
                messages.error(request, 'You must approve this task for public viewing to create it.')
                return redirect('post')
            
            # Create the task
            task = Task.objects.create(
                title=title,
                description=description,
                budget=budget,
                category=category,
                deadline=deadline if deadline else None,
                task_assigned_place=task_assigned_place,
                is_approved=is_approved,  # Set the approval status
                created_by=request.user
            )
            
            # This will trigger the clean() method in the model
            task.full_clean()
            
            messages.success(request, 'Task created successfully!')
            return redirect('profile')
                     
        except ValidationError as e:
            messages.error(request, f'Validation error: {", ".join(e.messages)}')
            return redirect('post')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')
            return redirect('post')
    
    return render(request, 'shop/post.html')

#----------------------------------------------------
@login_required
@require_GET
def study_material(request):
    """Display all study materials with filtering and pagination"""
    try:
        # Get filter parameters from request
        category = request.GET.get('category', 'all')
        material_type = request.GET.get('type', 'all')
        search_query = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort', 'latest')
        
        # Start with all materials
        queryset = StudyMaterial.objects.select_related('user').all()
        
        # Apply filters if specified
        if category != 'all':
            queryset = queryset.filter(category=category)
        
        if material_type != 'all':
            queryset = queryset.filter(material_type=material_type)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(task_assigned_place__icontains=search_query)
            )
        
        # Apply sorting
        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'most_viewed':
            queryset = queryset.order_by('-views', '-created_at')
        else:  # default sorting
            queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 12)  # 12 items per page
        page_number = request.GET.get('page')
        
        try:
            study_materials = paginator.page(page_number)
        except PageNotAnInteger:
            study_materials = paginator.page(1)
        except EmptyPage:
            study_materials = paginator.page(paginator.num_pages)
        
        # Prepare context
        context = {
            'study_materials': study_materials,
            'categories': StudyMaterial.CATEGORY_CHOICES,
            'material_types': StudyMaterial.MATERIAL_TYPE_CHOICES,
            'current_category': category,
            'current_type': material_type,
            'current_search': search_query,
            'current_sort': sort_by,
            'total_count': paginator.count,
        }
        
        return render(request, 'shop/study_material.html', context)
        
    except Exception as e:
        logger.error(f"Error loading study materials: {str(e)}", exc_info=True)
        messages.error(request, "Error loading study materials. Please try again.")
        
        # Return empty results on error
        return render(request, 'shop/study_material.html', {
            'study_materials': [],
            'categories': StudyMaterial.CATEGORY_CHOICES,
            'material_types': StudyMaterial.MATERIAL_TYPE_CHOICES,
            'current_category': 'all',
            'current_type': 'all',
            'current_search': '',
            'current_sort': 'latest',
            'total_count': 0,
        })

@login_required
@require_GET
def view_material(request, material_id):
    """View for displaying study material with view counting"""
    try:
        material = get_object_or_404(
            StudyMaterial.objects.select_related('user'), 
            id=material_id
        )
        
        # Record the view - you need to add this method to your StudyMaterial model
        # For now, let's increment views directly
        StudyMaterial.objects.filter(id=material_id).update(views=F('views') + 1)
        material.refresh_from_db()
        
        # Get related materials (same category, excluding current)
        related_materials = StudyMaterial.objects.filter(
            category=material.category
        ).exclude(id=material.id).order_by('-created_at')[:4]
        
        # Safe file size calculation
        try:
            file_size = material.file.size if material.file else 0
        except FileNotFoundError:
            file_size = 0
        
        context = {
            'material': material,
            'file_type': material.get_file_extension(),
            'file_size': file_size,
            'file_url': material.file.url if material.file else '',
            'total_views': material.views,
            'related_materials': related_materials,
        }
        return render(request, 'shop/view_material.html', context)
        
    except Exception as e:
        logger.error(f"Error in view_material: {str(e)}", exc_info=True)
        messages.error(request, "Error loading material. Please try again.")
        return render(request, 'shop/error/error.html', {
            'error_message': 'Material not found or unavailable.'
        })

@require_GET
def protected_file(request, material_id):
    """Serve protected files with security measures"""
    try:
        material = get_object_or_404(StudyMaterial, id=material_id)
        
        # Check permissions
        if not material.is_public and material.user != request.user:
            raise PermissionDenied("You don't have permission to access this file")
        
        # Check if file exists
        if not material.file:
            raise Http404("File not found")
        
        # Record view
        material.increment_views(request)
        
        # Determine content type
        ext = material.get_file_extension()
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        
        # Create secure response
        response = HttpResponse(content_type=content_type)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Security-Policy'] = "default-src 'self'"
        response['Cache-Control'] = 'private, max-age=3600'
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(material.file.name)}"'
        
        # Stream file content
        try:
            with material.file.open('rb') as f:
                response.write(f.read())
            return response
        except IOError:
            raise Http404("File not available")
            
    except PermissionDenied:
        raise
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in protected_file: {str(e)}", exc_info=True)
        raise Http404("File not available")

@require_GET
def ajax_get_material_stats(request, material_id):
    """Get material stats via AJAX"""
    try:
        material = get_object_or_404(StudyMaterial, id=material_id)
        
        # Check permissions
        if not material.is_public and material.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'total_views': material.views,
        })
    
    except StudyMaterial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Material not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error in ajax_get_material_stats: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request'
        }, status=500)

#-----------------------------------------------------------------------
@login_required
def apply_for_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if not Application.objects.filter(task=task, applicant=request.user).exists():
            Application.objects.create(
                task=task,
                applicant=request.user,
                message=message
            )
            messages.success(request, 'Application submitted successfully!')
        else:
            messages.warning(request, 'You have already applied for this task.')
        return redirect('base')
    
    return render(request, 'shop/apply_for_task.html', {'task': task})

@login_required
def my_task_applications(request):
    # Get all tasks created by the current user
    user_tasks = Task.objects.filter(created_by=request.user)
    
    # Get all applications for these tasks
    applications = Application.objects.filter(task__in=user_tasks).order_by('-applied_at')
    
    # Get notification counts for the bell icon
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    has_unread_notifications = unread_count > 0
    
    return render(request, 'shop/my_task_applications.html', {
        'applications': applications,
        'pending_count': applications.filter(status='pending').count(),
        'accepted_count': applications.filter(status='accepted').count(),
        'rejected_count': applications.filter(status='rejected').count(),
        'user_tasks': user_tasks,
        'unread_count': unread_count,
        'has_unread_notifications': has_unread_notifications,
    })

@require_POST
@login_required
def update_application_status(request, application_id, status):
    application = get_object_or_404(
        Application.objects.select_related('task', 'applicant'),
        id=application_id
    )
    
    if application.task.created_by != request.user:
        messages.error(request, "You don't have permission")
        return redirect('base')
    
    if status not in dict(Application.STATUS_CHOICES):
        messages.error(request, "Invalid status")
        return redirect('my_task_applications')
    
    # Update status and create notification
    with transaction.atomic():
        application.status = status
        application.save()
        
        # Create notification for applicant
        message = f"Your application for '{application.task.title}' has been {status}"
        Notification.objects.create(
            user=application.applicant,
            message=message,
            application=application,
        )
        
        messages.success(request, f"Application {status} and applicant notified")
    
    return redirect('my_task_applications')

@login_required
@require_POST
def delete_application(request, application_id):
    """Delete an application entry"""
    application = get_object_or_404(
        Application.objects.select_related('task', 'applicant'),
        id=application_id
    )
    
    # Check if the current user is the task creator (owner of the application)
    if application.task.created_by != request.user:
        messages.error(request, "You don't have permission to delete this application")
        return redirect('my_task_applications')
    
    try:
        # Store applicant and task info for notification
        applicant = application.applicant
        task_title = application.task.title
        
        # Create notification for applicant before deleting
        Notification.objects.create(
            user=applicant,
            message=f"Your application for '{task_title}' has been removed by the task creator",
        )
        
        # Delete the application
        application.delete()
        messages.success(request, 'Application deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting application: {str(e)}')
    
    return redirect('my_task_applications')

#---------------------------------------------------------------------------------------------
@login_required
def notifications(request):
    # Mark all unread as read when user opens notifications
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # For the bell icon (though it will be 0 after marking as read)
    unread_count = 0  # Since we just marked all as read
    
    return render(request, 'shop/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

# Optional: Add this API endpoint for real-time updates (mentioned in your JS)
from django.http import JsonResponse

@login_required
def notification_count_api(request):
    """API endpoint to get current notification count"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'unread_count': unread_count,
        'has_unread': unread_count > 0
    })

@require_POST
@login_required
def mark_notifications_read_api(request):
    """API endpoint to mark notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True}) 
#------------------------------------------
@login_required
def upload_study_material(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            category = request.POST.get('category')
            material_type = request.POST.get('material_type')
            task_assigned_place = request.POST.get('task_assigned_place', '')
            is_approved = request.POST.get('is_approved') == 'on'  # Handle checkbox
            
            file = request.FILES.get('file')
            
            # Validate required fields
            if not all([title, category, material_type, file]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('upload_study_material')
            
            # Check if user has agreed to approval terms (checkbox must be checked)
            if not is_approved:
                messages.error(request, 'You must approve this material for public viewing to upload.')
                return redirect('upload_study_material')
            
            # Validate file size based on material type
            max_sizes = {
                'pdf': 20 * 1024 * 1024,  # 20MB
                'image': 5 * 1024 * 1024,   # 5MB
            }
            
            if file.size > max_sizes.get(material_type, 10 * 1024 * 1024):
                messages.error(request, f'File size exceeds maximum allowed for {material_type}.')
                return redirect('upload_study_material')
            
            # Validate file type based on material type
            allowed_extensions = {
                'pdf': ['.pdf'],
                'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            }
            
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in allowed_extensions.get(material_type, []):
                messages.error(request, f'Invalid file type for {material_type}.')
                return redirect('upload_study_material')
            
            # Create study material
            study_material = StudyMaterial(
                user=request.user,
                title=title,
                description=description,
                category=category,
                material_type=material_type,
                task_assigned_place=task_assigned_place,
                file=file,
                is_approved=is_approved,  # Set the approval status
            )
            
            # This will trigger the clean() method in the model
            study_material.full_clean()
            study_material.save()
            
            messages.success(request, 'Study material uploaded successfully!')
            return redirect('study_material')
            
        except ValidationError as e:
            messages.error(request, f'Validation error: {", ".join(e.messages)}')
            return redirect('upload_study_material')
        except Exception as e:
            messages.error(request, f'Error uploading material: {str(e)}')
            return redirect('upload_study_material')
    
    # For GET requests, show the form with available choices
    context = {
        'material_type_choices': StudyMaterial.MATERIAL_TYPE_CHOICES,
        'category_choices': StudyMaterial.CATEGORY_CHOICES,
    }
    return render(request, 'shop/upload_study_material.html', context)

#-------------------- My Uploads --------------------
@login_required
def my_uploads(request):
    """Display all study materials uploaded by the current user"""
    try:
        # Get filter parameters from request
        category = request.GET.get('category', 'all')
        material_type = request.GET.get('type', 'all')
        search_query = request.GET.get('search', '').strip()
        
        # Start with user's materials
        queryset = StudyMaterial.objects.filter(user=request.user)
        
        # Apply filters if specified
        if category != 'all':
            queryset = queryset.filter(category=category)
        
        if material_type != 'all':
            queryset = queryset.filter(material_type=material_type)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Order by most recent first
        queryset = queryset.order_by('-created_at')
        
        # Calculate stats for the user
        # Pagination
        paginator = Paginator(queryset, 10)  # 10 items per page
        page_number = request.GET.get('page')
        
        try:
            user_materials = paginator.page(page_number)
        except PageNotAnInteger:
            user_materials = paginator.page(1)
        except EmptyPage:
            user_materials = paginator.page(paginator.num_pages)
        
        context = {
            'user_materials': user_materials,
            'categories': StudyMaterial.CATEGORY_CHOICES,
            'material_types': StudyMaterial.MATERIAL_TYPE_CHOICES,
            'current_category': category,
            'current_type': material_type,
            'current_search': search_query,
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
            'has_unread_notifications': Notification.objects.filter(
                user=request.user, is_read=False
            ).exists(),
        }
        
        return render(request, 'shop/my_uploads.html', context)
        
    except Exception as e:
        logger.error(f"Error in my_uploads view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading your uploads.")
        return render(request, 'shop/my_uploads.html')

@login_required
@require_POST
def delete_study_material(request, material_id):
    """Delete a study material"""
    material = get_object_or_404(StudyMaterial, id=material_id, user=request.user)
    
    try:
        # Delete the file from storage
        if material.file:
            default_storage.delete(material.file.name)
        
        # Delete the material record
        material.delete()
        messages.success(request, 'Study material deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error deleting material: {str(e)}')
    
    return redirect('my_uploads')

@login_required
def edit_study_material(request, material_id):
    """Edit an existing study material"""
    material = get_object_or_404(StudyMaterial, id=material_id, user=request.user)
    
    if request.method == 'POST':
        try:
            # Update fields
            material.title = request.POST.get('title', material.title)
            material.description = request.POST.get('description', material.description)
            material.category = request.POST.get('category', material.category)
            material.material_type = request.POST.get('material_type', material.material_type)
            material.task_assigned_place = request.POST.get('task_assigned_place', material.task_assigned_place)
            
            # Handle file update if provided
            if request.FILES.get('file'):
                # Delete old file if exists
                if material.file:
                    default_storage.delete(material.file.name)
                material.file = request.FILES['file']
            
            material.full_clean()
            material.save()
            
            messages.success(request, 'Study material updated successfully!')
            return redirect('my_uploads')
            
        except ValidationError as e:
            messages.error(request, f'Validation error: {", ".join(e.messages)}')
        except Exception as e:
            messages.error(request, f'Error updating material: {str(e)}')
    
    # For GET requests or failed POST, show the edit form
    context = {
        'material': material,
        'material_type_choices': StudyMaterial.MATERIAL_TYPE_CHOICES,
        'category_choices': StudyMaterial.CATEGORY_CHOICES,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'shop/edit_study_material.html', context)


#-------------------- Post Task --------------------
@login_required
def my_tasks(request):
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Count tasks by status
    assigned_count = tasks.filter(status='assigned').count()
    completed_count = tasks.filter(status='completed').count()
    
    context = {
        'tasks': tasks,
        'assigned_count': assigned_count,
        'completed_count': completed_count,
    }
    return render(request, 'shop/my_tasks.html', context)



@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    
    if request.method == 'POST':
        # Update task with form data
        task.title = request.POST.get('title', task.title)
        task.description = request.POST.get('description', task.description)
        task.budget = request.POST.get('budget', task.budget)
        task.category = request.POST.get('category', task.category)
        task.deadline = request.POST.get('deadline', task.deadline)
        task.task_assigned_place = request.POST.get('task_assigned_place', task.task_assigned_place)
        
        try:
            task.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('my_tasks')
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')
    
    return render(request, 'shop/edit_task.html', {'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            task.delete()
            messages.success(request, 'Task deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting task: {str(e)}')
    
    return redirect('my_tasks')

#--------------------------------------------
# views.py
@login_required
def user_directory(request):
    """Display all users with total count, search, and view tracking"""
    # Get base queryset with profile views
    users = User.objects.annotate(
        profile_views=Case(
            When(profile__views__isnull=False, then=F('profile__views')),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-profile_views')
    
    # Get total user count
    total_users = users.count()
    
    # Calculate active and new users
    today = timezone.now().date()
    one_week_ago = today - timedelta(days=7)
    
    active_count = User.objects.filter(last_login__date=today).count()
    new_count = User.objects.filter(date_joined__gte=one_week_ago).count()
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    
    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    context = {
        'users': users_page,
        'total_users': total_users,
        'active_count': active_count,
        'new_count': new_count,
        'search_query': search_query,
    }
    return render(request, 'shop/user_directory.html', context)

#-----------------------------------------------------
@login_required
def terms(request):
    """Terms and Conditions page view."""
    return render(request, 'shop/terms/terms.html')

#---------------------------------------------------
