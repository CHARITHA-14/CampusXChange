from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

# Optional PIL import for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def upload_to_posts(instance, filename):
    """Generate upload path for post images"""
    return f'posts/{instance.user.id}/{filename}'


def upload_to_requests(instance, filename):
    """Generate upload path for request images"""
    return f'requests/{instance.user.id}/{filename}'


def upload_to_profiles(instance, filename):
    """Generate upload path for profile pictures"""
    return f'profiles/{instance.user.id}/{filename}'


def upload_to_messages(instance, filename):
    """Generate upload path for message images"""
    return f'messages/{instance.conversation.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=50)
    branch = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.FileField(upload_to=upload_to_profiles, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    total_ratings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name or self.user.username}"

    def get_full_name(self):
        """Get user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    def get_display_name(self):
        """Get display name for the profile"""
        return self.user.first_name or self.user.username

    def get_rating_display(self):
        """Get formatted rating display"""
        if self.total_ratings > 0:
            return f"{self.rating:.1f}/5.0 ({self.total_ratings} ratings)"
        return "No ratings yet"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_picture and PIL_AVAILABLE:
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.profile_picture.path, optimize=True, quality=85)
            except Exception:
                # If image processing fails, continue without error
                pass

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For Font Awesome icons
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=200, blank=True, null=True)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    image = models.FileField(upload_to=upload_to_posts, blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.price}"

    def get_price_display(self):
        """Get formatted price display"""
        return f"₹{self.price}"

    def get_condition_display(self):
        """Get human-readable condition"""
        return dict(self.CONDITION_CHOICES).get(self.condition, self.condition)

    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def mark_as_sold(self):
        """Mark post as sold"""
        self.is_sold = True
        self.save(update_fields=['is_sold'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and PIL_AVAILABLE:
            try:
                img = Image.open(self.image.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, optimize=True, quality=85)
            except Exception:
                # If image processing fails, continue without error
                pass

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='additional_images', on_delete=models.CASCADE)
    image = models.FileField(upload_to='posts/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and PIL_AVAILABLE:
            try:
                img = Image.open(self.image.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, optimize=True, quality=85)
            except Exception:
                # If image processing fails, continue without error
                pass

class Request(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    location = models.CharField(max_length=200, blank=True, null=True)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    image = models.FileField(upload_to=upload_to_requests, blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    is_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - Budget: ₹{self.budget}"

    def get_budget_display(self):
        """Get formatted budget display"""
        return f"₹{self.budget}"

    def get_urgency_display(self):
        """Get human-readable urgency"""
        return dict(self.URGENCY_CHOICES).get(self.urgency, self.urgency)

    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def mark_as_fulfilled(self):
        """Mark request as fulfilled"""
        self.is_fulfilled = True
        self.save(update_fields=['is_fulfilled'])

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participants_names = ', '.join([user.username for user in self.participants.all()])
        context = ""
        if self.post:
            context = f" (Post: {self.post.title})"
        elif self.request:
            context = f" (Request: {self.request.title})"
        return f"Conversation between {participants_names}{context}"

    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()

    def get_last_message(self):
        """Get the last message in the conversation"""
        return self.messages.last()

    def get_unread_count(self, user):
        """Get unread message count for a user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def mark_messages_as_read(self, user):
        """Mark all messages as read for a user"""
        self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.FileField(upload_to=upload_to_messages, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

    def get_content_preview(self, max_length=50):
        """Get a preview of the message content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."

    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [['user', 'post'], ['user', 'request']]

    def __str__(self):
        item = self.post or self.request
        return f"{self.user.username} - {item.title if item else 'Unknown'}"

class Rating(models.Model):
    from_user = models.ForeignKey(User, related_name='ratings_given', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='ratings_received', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [['from_user', 'to_user', 'post'], ['from_user', 'to_user', 'request']]

    def __str__(self):
        return f"{self.from_user.username} rated {self.to_user.username} - {self.rating}/5"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('post_interest', 'Interest in Post'),
        ('request_response', 'Response to Request'),
        ('rating', 'New Rating'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    related_request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class Analytics(models.Model):
    date = models.DateField()
    total_users = models.PositiveIntegerField(default=0)
    total_posts = models.PositiveIntegerField(default=0)
    total_requests = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    new_posts = models.PositiveIntegerField(default=0)
    new_requests = models.PositiveIntegerField(default=0)
    new_messages = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['date']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.date}"
