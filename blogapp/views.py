from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
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

    def get_serializer_context(self):
        return {'request': self.request}

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in list view: {str(e)}")
            return Response(
                {"error": "Failed to fetch posts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in retrieve view: {str(e)}")
            return Response(
                {"error": "Failed to fetch post"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"POST data: {request.POST}")
            logger.debug(f"FILES data: {request.FILES}")
            
            if 'cover_image' in request.FILES:
                logger.info(f"Image found in request: {request.FILES['cover_image'].name}")
            else:
                logger.info("No image in request.FILES")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            instance = serializer.instance
            if instance.cover_image:
                logger.info(f"Image saved: {instance.cover_image.url}")
            else:
                logger.info("No image was saved")
                
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Error in create view: {str(e)}")
            return Response(
                {"error": "Failed to create post"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        try:
            if self.request.user.is_authenticated:
                serializer.save(author=self.request.user)
            else:
                from django.contrib.auth.models import User
                default_user = User.objects.first()
                if not default_user:
                    logger.error("No default user found")
                    raise Exception("No default user available")
                serializer.save(author=default_user)
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        try:
            post = self.get_object()
            related_posts = Post.objects.exclude(id=post.id)[:3]
            serializer = self.get_serializer(
                related_posts,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
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
                logger.error(f"Error sending email: {str(e)}")
                # Continue execution even if email fails
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"detail": "Your message has been sent successfully."},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Error in contact create view: {str(e)}")
            return Response(
                {"error": "Failed to send message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
