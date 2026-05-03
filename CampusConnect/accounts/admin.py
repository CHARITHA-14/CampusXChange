from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sessions.models import Session
from .models import (
    Profile, Category, Post, PostImage, Request, Conversation, 
    Message, Favorite, Rating, Notification, Analytics
)

# Inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('course', 'year', 'branch', 'phone_number', 'location', 'bio', 'profile_picture', 'is_verified', 'rating', 'total_ratings')
    readonly_fields = ('verification_token', 'created_at', 'last_active')

# Extend User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'year', 'branch', 'is_verified', 'rating', 'created_at')
    list_filter = ('is_verified', 'course', 'year', 'branch', 'created_at')
    search_fields = ('user__username', 'user__email', 'course', 'branch')
    readonly_fields = ('verification_token', 'created_at', 'last_active')
    ordering = ('-created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.action(description='Soft delete: mark selected posts inactive')
def soft_delete_posts(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'price', 'condition', 'is_featured', 'is_active', 'is_sold', 'views_count', 'created_at')
    list_filter = ('category', 'condition', 'is_active', 'is_sold', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [PostImageInline]
    list_editable = ('is_active', 'is_featured')
    actions = [soft_delete_posts]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

@admin.action(description='Soft delete: mark selected requests inactive')
def soft_delete_requests(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'budget', 'urgency', 'is_active', 'is_fulfilled', 'views_count', 'created_at')
    list_filter = ('category', 'urgency', 'is_active', 'is_fulfilled', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('is_active',)
    actions = [soft_delete_requests]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'created_at')
    ordering = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'post', 'request', 'created_at', 'is_active')
    list_filter = ('created_at', 'is_active')
    search_fields = ('participants__username',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item_title', 'get_item_type', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__title', 'request__title')
    
    def get_item_title(self, obj):
        return obj.post.title if obj.post else (obj.request.title if obj.request else 'N/A')
    get_item_title.short_description = 'Item Title'
    
    def get_item_type(self, obj):
        return 'Post' if obj.post else ('Request' if obj.request else 'N/A')
    get_item_type.short_description = 'Item Type'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'rating', 'get_item_title', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('from_user__username', 'to_user__username', 'review')
    readonly_fields = ('created_at',)
    
    def get_item_title(self, obj):
        return obj.post.title if obj.post else (obj.request.title if obj.request else 'N/A')
    get_item_title.short_description = 'Related Item'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_editable = ('is_read',)

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'total_posts', 'total_requests', 'new_users', 'new_posts', 'new_requests')
    list_filter = ('date',)
    ordering = ('-date',)
    readonly_fields = ('date',)

# Admin site branding
admin.site.site_header = 'CampusXChange Administration'
admin.site.site_title = 'CampusXChange Admin'
admin.site.index_title = 'Dashboard'

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date')
    list_filter = ('expire_date',)
    search_fields = ('session_key',)
