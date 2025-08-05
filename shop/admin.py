# shop/admin.py
from django.contrib import admin
from .models import Task, CustomUser,Profile, Education, Document, SocialLink,StudyMaterial

# Register your models here
admin.site.register(Task)
admin.site.register(CustomUser)
admin.site.register(StudyMaterial)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'views', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at', 'updated_at', 'views']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ( 'bio', 'location', 'phone', 'website')
        }),
        ('Images', {
            'fields': ('profile_picture', 'banner_image')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'degree', 'field_of_study', 'duration_display', 'created_at']
    list_filter = ['degree', 'start_date', 'end_date', 'created_at']
    search_fields = ['user__username', 'institution', 'degree', 'field_of_study']
    date_hierarchy = 'start_date'
    
    def duration_display(self, obj):
        return obj.duration
    duration_display.short_description = 'Duration'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Education Details', {
            'fields': ('institution', 'degree', 'field_of_study')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'document_type', 'file_size_display', 'is_public', 'uploaded_at']
    list_filter = ['document_type', 'is_public', 'uploaded_at']
    search_fields = ['title', 'user__username', 'description']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['file_size']
    
    def file_size_display(self, obj):
        return f"{obj.file_size_mb} MB" if obj.file_size_mb else "N/A"
    file_size_display.short_description = 'File Size'
    
    fieldsets = (
        ('Document Information', {
            'fields': ('user',  'document_type', 'description')
        }),
        ('File', {
            'fields': ('file', 'file_size')
        }),
        ('Settings', {
            'fields': ('is_public',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'username', 'is_public', 'created_at']
    list_filter = ['platform', 'is_public', 'created_at']
    search_fields = ['user__username', 'platform', 'username']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Social Link Details', {
            'fields': ('platform', 'username', 'url')
        }),
        ('Settings', {
            'fields': ('is_public',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    

