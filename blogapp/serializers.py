from rest_framework import serializers
from .models import Post, Contact
from django.conf import settings
import os

class PostSerializer(serializers.ModelSerializer):
    # Add a serialized field for the full image URL
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'excerpt', 'content', 'cover_image', 'cover_image_url', 'author', 'tags', 'published_at', 'updated_at']
        read_only_fields = ['slug', 'author', 'published_at', 'updated_at', 'cover_image_url']
    
    def get_cover_image_url(self, obj):
        """Return the complete URL for the cover image"""
        if obj.cover_image and obj.cover_image.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            # Make sure we return an absolute URL, not just the relative path
            media_url = settings.MEDIA_URL.rstrip('/')
            base_url = "http://localhost:8000"  # Fallback if request is not available
            return f"{base_url}{media_url}/{obj.cover_image}"
        
        # Return a default placeholder image URL
        request = self.context.get('request')
        if request:
            # Check if the placeholder exists, create it if not
            placeholder_path = os.path.join(settings.MEDIA_ROOT, 'posts', 'placeholder.jpg')
            if not os.path.exists(placeholder_path):
                os.makedirs(os.path.dirname(placeholder_path), exist_ok=True)
                with open(placeholder_path, 'w') as f:
                    pass  # Create empty file
            
            return request.build_absolute_uri(f"{settings.MEDIA_URL}posts/placeholder.jpg")
        
        # Fallback with absolute URL
        return f"http://localhost:8000{settings.MEDIA_URL}posts/placeholder.jpg"

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at'] 