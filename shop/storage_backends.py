"""
Create this file: shop/storage_backends.py
Custom Django storage backend for Supabase Storage
"""

import os
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin
import mimetypes


@deconstructible
class SupabaseStorage(Storage):
    """
    Custom storage backend for Supabase Storage
    """
    
    def __init__(self, **settings_dict):
        super().__init__(**settings_dict)
        self.supabase_url = getattr(settings, 'SUPABASE_URL')
        self.supabase_key = getattr(settings, 'SUPABASE_KEY')
        self.bucket = getattr(settings, 'SUPABASE_BUCKET', 'media')
        self.base_url = f'{self.supabase_url}/storage/v1/object'
        
    def _get_headers(self):
        """Get headers for Supabase API requests"""
        return {
            'Authorization': f'Bearer {self.supabase_key}',
            'apikey': self.supabase_key,
        }
    
    def _save(self, name, content):
        """
        Save file to Supabase Storage
        """
        # Ensure the content is at the beginning
        content.seek(0)
        
        # Prepare the file data
        files = {
            'file': (name, content.read(), self._get_content_type(name))
        }
        
        # Upload URL
        upload_url = f'{self.base_url}/{self.bucket}/{name}'
        
        try:
            response = requests.post(
                upload_url,
                files=files,
                headers=self._get_headers()
            )
            
            if response.status_code in [200, 201]:
                return name
            else:
                raise Exception(f'Supabase upload failed: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error uploading to Supabase: {str(e)}')
    
    def _open(self, name, mode='rb'):
        """
        Open and return a file from Supabase Storage
        """
        file_url = self.url(name)
        
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                return ContentFile(response.content, name=name)
            else:
                raise Exception(f'File not found: {name}')
        except Exception as e:
            raise Exception(f'Error opening file from Supabase: {str(e)}')
    
    def exists(self, name):
        """
        Check if file exists in Supabase Storage
        """
        file_url = f'{self.base_url}/{self.bucket}/{name}'
        
        try:
            response = requests.head(
                file_url,
                headers=self._get_headers()
            )
            return response.status_code == 200
        except:
            return False
    
    def delete(self, name):
        """
        Delete file from Supabase Storage
        """
        delete_url = f'{self.base_url}/{self.bucket}/{name}'
        
        try:
            response = requests.delete(
                delete_url,
                headers=self._get_headers()
            )
            return response.status_code in [200, 204]
        except:
            return False
    
    def url(self, name):
        """
        Return URL for accessing the file
        """
        return f'{self.supabase_url}/storage/v1/object/public/{self.bucket}/{name}'
    
    def size(self, name):
        """
        Return file size
        """
        try:
            response = requests.head(self.url(name))
            return int(response.headers.get('Content-Length', 0))
        except:
            return 0
    
    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's available for use
        """
        if not self.exists(name):
            return name
        
        # If file exists, append timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_part, ext = os.path.splitext(name)
        return f"{name_part}_{timestamp}{ext}"
    
    def _get_content_type(self, name):
        """
        Get content type for file
        """
        content_type, _ = mimetypes.guess_type(name)
        return content_type or 'application/octet-stream'


@deconstructible
class SupabaseStaticStorage(SupabaseStorage):
    """
    Storage backend for static files using Supabase
    """
    
    def __init__(self, **settings_dict):
        super().__init__(**settings_dict)
        self.bucket = 'static'  # Use different bucket for static files