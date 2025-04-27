from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid
from datetime import datetime

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField()
    content = models.TextField()
    cover_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.JSONField(default=list)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug by appending a timestamp
            base_slug = slugify(self.title)
            # Add a timestamp to ensure uniqueness
            unique_id = datetime.now().strftime('%Y%m%d%H%M%S')
            self.slug = f"{base_slug}-{unique_id}"
            
        # Print info about the image being saved
        if hasattr(self, 'cover_image') and self.cover_image:
            print(f"Cover image before save: {self.cover_image}")
            
        super().save(*args, **kwargs)
        
        # Print info after save
        if hasattr(self, 'cover_image') and self.cover_image:
            print(f"Cover image after save: {self.cover_image}")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']
