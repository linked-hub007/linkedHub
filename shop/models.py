# shop/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import date
import os
import datetime
from django.db.models import F
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone

def get_upload_path(instance, filename):
    now = datetime.datetime.now().strftime("%Y/%m/%d")
    folder = 'task_attachments'
    return os.path.join(folder, now, filename)

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username

class Task(models.Model):
    STATUS_CHOICES = [
        ('posted', 'Posted'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('urgent', 'Urgent'),
        ('delivery', 'Delivery'),
        ('cleaning', 'Cleaning'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tasks_created'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tasks_assigned'
    )
    budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)], 
        default=0.01
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='posted')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    task_assigned_place = models.TextField(
        blank=True,
        null=True,
        verbose_name="Assigned Place (School/College/Company)",
        help_text="E.g., 'Harvard University', 'Google Inc', 'ABC School'",
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Approved",
        help_text="Check this box to approve the task for public viewing"
    )
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Task.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.deadline and self.deadline < date.today():
            raise ValidationError({'deadline': "Deadline cannot be in the past."})
        if self.budget <= 0:
            raise ValidationError({'budget': "Budget must be a positive number."})
        if self.assigned_to and self.status == 'posted':
            raise ValidationError({'status': "Cannot assign a user when status is 'posted'."})
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'slug': self.slug})

#----------------------------------------------------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='banner_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    title = models.CharField(max_length=100, blank=True, verbose_name="Professional Title")
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.user.pk})

    class Meta:
        ordering = ['-created_at']


class Education(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

    @property
    def duration(self):
        if self.end_date:
            return f"{self.start_date.year} - {self.end_date.year}"
        return f"{self.start_date.year} - Present"

    class Meta:
        ordering = ['-start_date']


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('resume', 'Resume/CV'),
        ('certificate', 'Certificate'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    file_size = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    class Meta:
        ordering = ['-uploaded_at']


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('website', 'Personal Website'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    username = models.CharField(max_length=100)
    url = models.URLField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.username}"

    @property
    def icon_class(self):
        icon_mapping = {
            'linkedin': 'fab fa-linkedin',
            'github': 'fab fa-github',
            'twitter': 'fab fa-twitter',
            'instagram': 'fab fa-instagram',
            'website': 'fas fa-globe',
            'youtube': 'fab fa-youtube',
            'facebook': 'fab fa-facebook',
            'other': 'fas fa-link'
        }
        return icon_mapping.get(self.platform, 'fas fa-link')

    class Meta:
        ordering = ['platform']
        unique_together = ['user', 'platform', 'username']

#----------------------------------------------------------------------------------------------
class StudyMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('image', 'Image'),
    ]
    
    CATEGORY_CHOICES = [
        ('all', 'All'),
        ('school_qp', 'School Question Papers'),
        ('college_qp', 'College Question Papers'),
        ('competitive_exam', 'Competitive Exams'),
        ('entrance_exam', 'Entrance Exams'),
        ('eligibility_test', 'Eligibility Test'),
        ('books', 'Books'),
        ('sample_paper', 'Sample Papers'),
        ('notes', 'Notes'),
        ('other', 'Other'),
    ]
    
    EXTENSION_MAPPING = {
        'pdf': ['pdf'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    }
    
    MAX_FILE_SIZES = {
        'pdf': 20 * 1024 * 1024,  # 20MB
        'image': 5 * 1024 * 1024,  # 5MB
    }
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_assigned_place = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Institution/Organization"
    )
    file = models.FileField(
        upload_to='study_materials/%Y/%m/',
        help_text="Upload PDF or image files only"
    )
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Approved",
        help_text="Check this box to approve the material for public viewing"
    )
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Study Material'
        verbose_name_plural = 'Study Materials'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['material_type']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"
    
    def get_absolute_url(self):
        return reverse('view_material', kwargs={'material_id': self.pk})
    
    def get_file_extension(self):
        """Get lowercase file extension without the dot"""
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].lower()
        return ''
    
    def clean(self):
        """Validate file type and size"""
        super().clean()
        
        if self.file:
            ext = self.get_file_extension()
            allowed_extensions = self.EXTENSION_MAPPING.get(self.material_type, [])
            
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"Invalid file type for {self.get_material_type_display()}. "
                    f"Allowed extensions: {', '.join(allowed_extensions)}"
                )
            
            max_size = self.MAX_FILE_SIZES.get(self.material_type)
            if max_size and self.file.size > max_size:
                raise ValidationError(
                    f"File too large. Maximum size for {self.material_type} is {max_size/1024/1024}MB"
                )


class MaterialView(models.Model):
    """Detailed view tracking for study materials"""
    study_material = models.ForeignKey(
        StudyMaterial, 
        on_delete=models.CASCADE, 
        related_name='material_views'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'Material View'
        verbose_name_plural = 'Material Views'
        indexes = [
            models.Index(fields=['study_material']),
            models.Index(fields=['user']),
            models.Index(fields=['viewed_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"View of {self.study_material} by {self.user or 'Anonymous'}"

#-----------------------------------------------------------------------------
class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ('applicant', 'task')
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.task.title}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

#----------------------------------------------------------------------------------------------
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.CharField(max_length=255)
    application = models.ForeignKey(
        'Application', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

#----------------------------------------------------------------------------------
