

# shop/urls.py
from django.urls import path, include
from . import views
from . import otp_views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from allauth.account.views import ConfirmEmailView   
from .views import create_task, view_material

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('base/', views.base, name='base'),
    path('post/', views.post, name='post'),
    path('settings/', views.settings, name='settings'),   
    path('logout/', views.logout_page, name='logout'),
    
    path(r'^images/(?P<path>.*)$', views.serve_media, name='serve_media'),
    # User directory
    path('users/', views.user_directory, name='user_directory'),

    # Task related URLs
    path('create-task/', create_task, name='create_task'),
    path('task/<int:task_id>/apply/', views.apply_for_task, name='apply_for_task'),
    path('my-task-applications/', views.my_task_applications, name='my_task_applications'),
    path('my-task-applications/delete/<int:application_id>/', views.delete_application, name='delete_application'),
    path('application/<int:application_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('profile/my-tasks/', views.my_tasks, name='my_tasks'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),

    # Study material URLs
    path('study-materials/', views.study_material, name='study_material'),
    path('profile/post_study', views.upload_study_material, name='upload_study_material'),
    path('material/<int:material_id>/', views.view_material, name='view_material'),
    path('protected-file/<int:material_id>/', views.protected_file, name='protected_file'),
    path('material/<int:material_id>/stats/', views.ajax_get_material_stats, name='material_stats'),
    path('my-uploads/', views.my_uploads, name='my_uploads'),
    path('study-material/<int:material_id>/delete/', views.delete_study_material, name='delete_study_material'),
    path('study-material/<int:material_id>/edit/', views.edit_study_material, name='edit_study_material'),

    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('api/notification-count/', views.notification_count_api, name='notification_count_api'),
    path('api/mark-notifications-read/', views.mark_notifications_read_api, name='mark_notifications_read_api'),

    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/post_task', views.post, name='post'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),
    path('profile/<int:pk>/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/settings/', views.account_settings, name='account_settings'),
    path('profile/increment-views/', views.increment_profile_views, name='increment_profile_views'),

    # Document management
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),

    # Social links management
    path('social-links/add/', views.add_social_link, name='add_social_link'),
    path('social-links/<int:link_id>/delete/', views.delete_social_link, name='delete_social_link'),

    # Education management
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:education_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:education_id>/delete/', views.delete_education, name='delete_education'),

    # OTP URLs
    path('send-otp/', otp_views.send_otp, name='send_otp'),
    path('setup-otp/', otp_views.setup_otp, name='setup_otp'),
    path('verify-otp/', otp_views.verify_otp, name='verify_otp'),
    # Terms 
    path('terms/', views.terms, name='terms'),
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
    path('password/change/',auth_views.PasswordChangeView.as_view(template_name='registration/change_password.html',success_url='/password/change/done/'),name='change_password'),
    path('password/change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='registration/change_password_done.html'),name='change_password_done'),
     
    # Allauth URLs
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

