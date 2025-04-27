from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Contact
from .serializers import PostSerializer, ContactSerializer

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to create posts
    lookup_field = 'slug'

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        return context  # This already includes the request

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        
        # Debug image URLs
        data = serializer.data
        print(f"Image data in API response: cover_image={data.get('cover_image')}, cover_image_url={data.get('cover_image_url')}")
        
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Override create to handle file uploads properly"""
        # Print debug info about the incoming request
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Verify the image is in the request
        if 'cover_image' in request.FILES:
            print(f"Image found in request: {request.FILES['cover_image'].name}")
        else:
            print("No image in request.FILES")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the created instance and check the image field
        instance = serializer.instance
        if instance.cover_image:
            print(f"Image saved: {instance.cover_image.url}")
        else:
            print("No image was saved")
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # For anonymous users, use a default user or set to None
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            # Get the first user as default author or handle as needed
            from django.contrib.auth.models import User
            default_user = User.objects.first()
            serializer.save(author=default_user)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        post = self.get_object()
        related_posts = Post.objects.exclude(id=post.id)[:3]
        serializer = self.get_serializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    http_method_names = ['post']  # Only allow POST requests
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send email notification
        contact_data = serializer.validated_data
        email_subject = f"Blog Contact: {contact_data['subject']}"
        email_message = f"""
        New contact form submission:
        
        Name: {contact_data['name']}
        Email: {contact_data['email']}
        Subject: {contact_data['subject']}
        
        Message:
        {contact_data['message']}
        """
        
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['tamboliaftab84@gmail.com'],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error sending email: {str(e)}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"detail": "Your message has been sent successfully."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
