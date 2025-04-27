import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp_api.settings')
django.setup()

from django.contrib.auth.models import User
from blogapp.models import Post

# Create a test user if one doesn't exist
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("Created test user 'admin'")
else:
    user = User.objects.get(username='admin')
    print("Using existing user 'admin'")

# Create sample posts
sample_posts = [
    {
        'title': 'Getting Started with React',
        'excerpt': 'Learn the basics of React and build your first app.',
        'content': '<p>React is a JavaScript library for building user interfaces. It makes it painless to create interactive UIs. Design simple views for each state in your application, and React will efficiently update and render just the right components when your data changes.</p><p>Declarative views make your code more predictable and easier to debug.</p>',
        'tags': ['react', 'javascript', 'frontend']
    },
    {
        'title': 'Introduction to Django REST Framework',
        'excerpt': 'Build powerful APIs with Django REST Framework.',
        'content': '<p>Django REST framework is a powerful and flexible toolkit for building Web APIs. Some reasons you might want to use REST framework:</p><ul><li>The Web browsable API is a huge usability win for your developers.</li><li>Authentication policies including packages for OAuth1a and OAuth2.</li><li>Serialization that supports both ORM and non-ORM data sources.</li></ul>',
        'tags': ['django', 'python', 'backend', 'api']
    },
    {
        'title': 'Creating a Modern Blog with React and Django',
        'excerpt': 'A comprehensive guide to building a modern blog with React and Django.',
        'content': '<p>In this tutorial, we will build a modern blog application using React for the frontend and Django for the backend. We will cover everything from setting up the project to deploying it to production.</p><p>The blog will have features like user authentication, comments, and a rich text editor for writing posts.</p>',
        'tags': ['react', 'django', 'fullstack', 'tutorial']
    },
    {
        'title': 'Modern CSS Techniques',
        'excerpt': 'Learn about modern CSS techniques like Flexbox and Grid.',
        'content': '<p>CSS has come a long way since its inception. With modern features like Flexbox and Grid, we can create complex layouts with ease.</p><p>In this article, we will explore some of the most powerful CSS techniques that you can use in your projects today.</p>',
        'tags': ['css', 'frontend', 'web design']
    },
    {
        'title': 'The Power of TailwindCSS',
        'excerpt': 'Discover why TailwindCSS is becoming so popular among developers.',
        'content': '<p>TailwindCSS is a utility-first CSS framework packed with classes like flex, pt-4, text-center, and rotate-90 that can be composed to build any design, directly in your markup.</p><p>Instead of opinionated predesigned components, Tailwind provides low-level utility classes that let you build completely custom designs without ever leaving your HTML.</p>',
        'tags': ['css', 'tailwind', 'frontend']
    }
]

for post_data in sample_posts:
    post, created = Post.objects.get_or_create(
        title=post_data['title'],
        defaults={
            'excerpt': post_data['excerpt'],
            'content': post_data['content'],
            'tags': post_data['tags'],
            'author': user
        }
    )
    
    if created:
        print(f"Created post: {post.title}")
    else:
        print(f"Post already exists: {post.title}")

print("\nSample posts have been created successfully!") 