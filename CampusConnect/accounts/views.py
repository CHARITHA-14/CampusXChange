from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Profile, Notification, Conversation, Message, Post, Request, Category
from .forms import CustomUserRegisterForm, ProfileEditForm, UserEditForm, CustomAuthenticationForm
from decimal import Decimal

def home(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, type='message', is_read=False).count()
    return render(request, 'accounts/home.html', { 'unread_chat_count': unread_count })

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Please verify your email address before logging in. Check your email for a verification link.')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
@never_cache
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {username}! You have been logged out successfully.')
    return redirect('home')

@login_required
@never_cache
def homepage(request):
    return render(request, "accounts/homepage.html")

@login_required
@never_cache
def categories(request):
    from .models import Category

    # Auto-populate categories if none exist (runs only once when DB is empty)
    if not Category.objects.exists():
        default_categories = [
            {'name': 'Books', 'slug': 'books', 'description': 'Academic books, novels, reference materials', 'icon': '📚'},
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Laptops, phones, gadgets, accessories', 'icon': '💻'},
            {'name': 'Stationery', 'slug': 'stationery', 'description': 'Pens, notebooks, calculators, art supplies', 'icon': '✏️'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Formal wear, casual clothes, accessories', 'icon': '👕'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment, gym gear, outdoor items', 'icon': '⚽'},
            {'name': 'Furniture', 'slug': 'furniture', 'description': 'Chairs, tables, study desks, storage', 'icon': '🪑'},
            {'name': 'Kitchen', 'slug': 'kitchen', 'description': 'Cookware, utensils, appliances', 'icon': '🍳'},
            {'name': 'Others', 'slug': 'others', 'description': 'Miscellaneous items and accessories', 'icon': '📦'},
        ]
        for cat_data in default_categories:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'is_active': True
                }
            )

    cats = Category.objects.filter(is_active=True).order_by('name')
    return render(request, "accounts/categories.html", {"categories": cats})

@login_required
@never_cache
def category_detail(request, category):
    """Display posts and requests for a specific category identified by slug."""
    from .models import Post, Request, Category
    
    # Resolve slug to Category object
    category_obj = get_object_or_404(Category, slug=category)
    
    # Get posts and requests for the resolved category
    posts = Post.objects.filter(category=category_obj, is_active=True).order_by('-created_at')
    requests = Request.objects.filter(category=category_obj, is_active=True).order_by('-created_at')
    
    context = {
        'category': category_obj.slug,
        'category_display': category_obj.name,
        'posts': posts,
        'requests': requests,
    }
    
    return render(request, 'accounts/category_detail.html', context)

@login_required
@never_cache
def chats(request):
    active_conversation_id = request.GET.get('conversation_id')
    return render(request, "accounts/chats.html", { 'active_conversation_id': active_conversation_id })

@login_required
@never_cache
def old_requests(request):
    from .models import Post, Request, Category
    
    # Get user's posts and requests
    user_posts = Post.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    user_requests = Request.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'user_posts': user_posts,
        'user_requests': user_requests,
        'categories': categories,
    }
    
    return render(request, "accounts/old_requests.html", context)

@login_required
@never_cache
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Count user's posts and requests
    posts_count = request.user.posts.filter(is_active=True).count()
    requests_count = request.user.requests.filter(is_active=True).count()
    
    context = {
        'profile': profile,
        'posts_count': posts_count,
        'requests_count': requests_count,
    }
    return render(request, "accounts/profile.html", context)

@login_required
@never_cache
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    })

@login_required
@never_cache
def create_post(request):
    """Create a new post"""
    from decimal import Decimal, InvalidOperation
    from .models import Post, Category

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        price_raw = (request.POST.get('price') or '').strip()
        category_slug = (request.POST.get('category') or '').strip()
        condition = (request.POST.get('condition') or '').strip()
        image_file = request.FILES.get('image')

        # Normalize condition value from UI to model choices
        if condition == 'like-new':
            condition = 'like_new'

        # Basic validation
        if not (title and description and price_raw and category_slug and condition):
            messages.error(request, 'Please fill in all fields.')
            return redirect('old_requests')

        # Convert price
        try:
            price = Decimal(price_raw)
        except (InvalidOperation, ValueError):
            messages.error(request, 'Invalid price format.')
            return redirect('old_requests')

        # Resolve category by slug
        try:
            category_obj = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            messages.error(request, 'Selected category does not exist.')
            return redirect('old_requests')

        Post.objects.create(
            user=request.user,
            title=title,
            description=description,
            price=price,
            category=category_obj,
            condition=condition,
            image=image_file if image_file else None,
        )
        messages.success(request, 'Post created successfully!')
        return redirect('old_requests')

    return redirect('old_requests')

@login_required
@never_cache
def create_request(request):
    """Create a new request"""
    from decimal import Decimal, InvalidOperation
    from .models import Request, Category

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = (request.POST.get('description') or '').strip()
        budget_raw = (request.POST.get('budget') or '').strip()
        category_slug = (request.POST.get('category') or '').strip()
        urgency = (request.POST.get('urgency') or '').strip()
        image_file = request.FILES.get('image')

        if not (title and description and budget_raw and category_slug and urgency):
            messages.error(request, 'Please fill in all fields.')
            return redirect('old_requests')

        try:
            budget = Decimal(budget_raw)
        except (InvalidOperation, ValueError):
            messages.error(request, 'Invalid budget format.')
            return redirect('old_requests')

        try:
            category_obj = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            messages.error(request, 'Selected category does not exist.')
            return redirect('old_requests')

        Request.objects.create(
            user=request.user,
            title=title,
            description=description,
            budget=budget,
            category=category_obj,
            urgency=urgency,
            image=image_file if image_file else None,
        )
        messages.success(request, 'Request created successfully!')
        return redirect('old_requests')

    return redirect('old_requests')

@login_required
@never_cache
def delete_post(request, post_id):
    """Delete a post"""
    from .models import Post
    
    try:
        post = Post.objects.get(id=post_id, user=request.user)
        post.is_active = False
        post.save()
        messages.success(request, 'Post deleted successfully!')
    except Post.DoesNotExist:
        messages.error(request, 'Post not found.')
    
    return redirect('old_requests')

@login_required
@never_cache
def delete_request(request, request_id):
    """Delete a request"""
    from .models import Request
    
    try:
        req = Request.objects.get(id=request_id, user=request.user)
        req.is_active = False
        req.save()
        messages.success(request, 'Request deleted successfully!')
    except Request.DoesNotExist:
        messages.error(request, 'Request not found.')
    
    return redirect('old_requests')


def send_verification_email(user):
    """Send verification email to user"""
    subject = 'Verify Your CampusXChange Account'
    html_message = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_url': f"{settings.SITE_URL}/verify-email/{user.profile.verification_token}/"
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def register(request):
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been created! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    """Verify user email with token"""
    try:
        profile = Profile.objects.get(verification_token=token)
        user = profile.user
        user.is_active = True
        user.save()
        profile.is_verified = True
        profile.save()
        messages.success(request, "Your email has been verified successfully! You can now log in.")
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('home')

# Chat Views
@login_required
def conversations_list(request):
    """Get list of conversations for the current user"""
    conversations = Conversation.objects.filter(participants=request.user, is_active=True).order_by('-updated_at')
    
    conversations_data = []
    for conv in conversations:
        last_message = conv.get_last_message()
        other_participant = conv.get_other_participant(request.user)
        context_type = 'item' if conv.post_id else ('request' if conv.request_id else '')
        context_title = conv.post.title if conv.post_id else (conv.request.title if conv.request_id else '')
        
        conversations_data.append({
            'id': conv.id,
            'participants': [p.username for p in conv.participants.all()],
            'last_message': {
                'content': last_message.content if last_message else '',
                'sender_username': last_message.sender.username if last_message else '',
                'created_at': last_message.created_at.isoformat() if last_message else None
            } if last_message else None,
            'other_participant': other_participant.username if other_participant else '',
            'unread_count': conv.get_unread_count(request.user),
            'context_type': context_type,
            'context_title': context_title
        })
    
    return JsonResponse(conversations_data, safe=False)

@login_required
def conversation_messages(request, conversation_id):
    """Get messages for a specific conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    
    # Mark messages as read
    conversation.mark_messages_as_read(request.user)
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_username': msg.sender.username,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        })
    
    return JsonResponse(messages_data, safe=False)

@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Send a message to a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save()
        
        return JsonResponse({
            'id': message.id,
            'content': message.content,
            'sender_username': message.sender.username,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def start_conversation(request, user_id):
    """Start a conversation with another user"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        return JsonResponse({'error': 'Cannot start conversation with yourself'}, status=400)
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return JsonResponse({'conversation_id': existing_conversation.id})
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return JsonResponse({'conversation_id': conversation.id})



# Item Interest and Request Response Views
@login_required
@require_http_methods(["POST"])
def express_interest(request, item_id):
    """Express interest in an item and create conversation"""
    from .models import Post
    
    try:
        item = get_object_or_404(Post, id=item_id, is_active=True)
        
        # Don't allow users to express interest in their own items
        if item.user == request.user:
            return JsonResponse({'error': 'Cannot express interest in your own item'}, status=400)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=item.user
        ).filter(
            post=item
        ).first()
        
        if existing_conversation:
            conversation_id = existing_conversation.id
        else:
            # Create new conversation
            conversation = Conversation.objects.create(post=item)
            conversation.participants.add(request.user, item.user)
            conversation_id = conversation.id
            
            # Add initial message if provided
            data = json.loads(request.body) if request.body else {}
            message = data.get('message', '').strip()
            if message:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=message
                )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation started successfully!'
        })
            
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def respond_to_request(request, request_id):
    """Respond to a request and create conversation"""
    from .models import Request
    
    try:
        req = get_object_or_404(Request, id=request_id, is_active=True)
        
        # Don't allow users to respond to their own requests
        if req.user == request.user:
            return JsonResponse({'error': 'Cannot respond to your own request'}, status=400)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=req.user
        ).filter(
            request=req
        ).first()
        
        if existing_conversation:
            conversation_id = existing_conversation.id
        else:
            # Create new conversation
            conversation = Conversation.objects.create(request=req)
            conversation.participants.add(request.user, req.user)
            conversation_id = conversation.id
            
            # Add initial message if provided
            data = json.loads(request.body) if request.body else {}
            message = data.get('message', '').strip()
            if message:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=message
                )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation started successfully!'
        })
            
    except Request.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Enhanced send_message view with email notifications
@login_required
@require_http_methods(["POST"])
def send_message_enhanced(request, conversation_id):
    """Send a message to a conversation with email notification"""
    from .utils import send_message_notification
    
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save()
        
        # Send email notification to the other participant
        other_participant = conversation.get_other_participant(request.user)
        if other_participant:
            # Send email notification (fail silently to not interrupt chat flow)
            try:
                send_message_notification(message, other_participant)
            except Exception:
                pass  # Don't let email failures interrupt the chat
        
        return JsonResponse({
            'id': message.id,
            'content': message.content,
            'sender_username': message.sender.username,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Simple web-based views only
