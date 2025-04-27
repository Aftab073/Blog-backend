from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from .models import Post, Contact
from .serializers import PostSerializer, ContactSerializer
import logging

# Set up logger
logger = logging.getLogger('blogapp')

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        try:
            return Post.objects.all().select_related('author')
        except DatabaseError as e:
            logger.error(f"Database error in get_queryset: {str(e)}")
            raise

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except DatabaseError as e:
            logger.error(f"Database error in list view: {str(e)}")
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in list view: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                logger.info(f"Creating new post with data: {request.data}")
                
                # Validate image if present
                if 'cover_image' in request.FILES:
                    image = request.FILES['cover_image']
                    if image.size > 5 * 1024 * 1024:  # 5MB limit
                        raise ValidationError("Image size should not exceed 5MB")
                
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
                
        except ValidationError as e:
            logger.error(f"Validation error in create view: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(f"Database error in create view: {str(e)}")
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in create view: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        try:
            if self.request.user.is_authenticated:
                serializer.save(author=self.request.user)
            else:
                from django.contrib.auth.models import User
                default_user = User.objects.filter(is_superuser=True).first()
                if not default_user:
                    logger.error("No default user found")
                    raise ValidationError("No default user available")
                serializer.save(author=default_user)
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        try:
            post = self.get_object()
            # Get posts with similar tags
            related_posts = Post.objects.filter(tags__overlap=post.tags)\
                .exclude(id=post.id)\
                .distinct()[:3]
            
            if not related_posts:
                # If no posts with similar tags, get most recent posts
                related_posts = Post.objects.exclude(id=post.id)[:3]
                
            serializer = self.get_serializer(related_posts, many=True)
            return Response(serializer.data)
        except DatabaseError as e:
            logger.error(f"Database error in related posts view: {str(e)}")
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error in related posts view: {str(e)}")
            return Response(
                {"error": "Failed to fetch related posts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                logger.info(f"Processing contact form submission: {request.data}")
                
                serializer = self.get_serializer(data=request.data)
                if not serializer.is_valid():
                    logger.error(f"Contact form validation errors: {serializer.errors}")
                    return Response(
                        {"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
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
                        recipient_list=[settings.DEFAULT_FROM_EMAIL],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Error sending email notification: {str(e)}")
                    # Log but don't fail the request if email fails
                
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {"detail": "Your message has been sent successfully."},
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
                
        except DatabaseError as e:
            logger.error(f"Database error in contact create: {str(e)}")
            return Response(
                {"error": "Database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in contact create: {str(e)}")
            return Response(
                {"error": "Failed to send message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
