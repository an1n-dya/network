from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MaxLengthValidator
from django.urls import reverse


class User(AbstractUser):
    """Extended User model with additional social features"""
    bio = models.TextField(max_length=160, blank=True, help_text="Tell us about yourself")
    avatar = models.URLField(blank=True, help_text="Profile picture URL")
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})
    
    def follower_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.following.count()
    
    def posts_count(self):
        return self.posts.count()
    
    def __str__(self):
        return self.username


class Post(models.Model):
    """Post model with enhanced features"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(
        max_length=280,
        validators=[MaxLengthValidator(280)],
        help_text="What's on your mind? (280 characters max)"
    )
    timestamp = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    
    # Enhanced features
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    image = models.URLField(blank=True, help_text="Optional image URL")
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    
    # Engagement metrics
    views = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}..."

    @property
    def like_count(self):
        return self.likes.count()
    
    def reply_count(self):
        return self.replies.count()
    
    def is_reply(self):
        return self.reply_to is not None
    
    


class Follow(models.Model):
    """Follow relationship model"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Notification settings
    notifications_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Notification(models.Model):
    """Notification system"""
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('reply', 'Reply'),
        ('mention', 'Mention'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"


class HashTag(models.Model):
    """Hashtag model for trending topics"""
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, related_name="hashtags", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"#{self.name}"
    
    def posts_count(self):
        return self.posts.count()


class UserSession(models.Model):
    """Track user sessions for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        unique_together = ('user', 'session_key')

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


class APIKey(models.Model):
    """API keys for external integrations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"
