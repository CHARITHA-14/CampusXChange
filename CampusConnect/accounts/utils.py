from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def send_item_request_notification(item, requester, item_owner, message=None):
    """
    Send email notification to item owner when someone requests their item
    """
    try:
        # Create conversation for chat
        from .models import Conversation
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=requester
        ).filter(
            participants=item_owner
        ).filter(
            post=item
        ).first()
        
        if not existing_conversation:
            # Create new conversation
            conversation = Conversation.objects.create(post=item)
            conversation.participants.add(requester, item_owner)
        else:
            conversation = existing_conversation
        
        # Prepare email context
        context = {
            'item': item,
            'item_owner': item_owner,
            'requester': requester,
            'message': message,
            'chat_url': f"{settings.SITE_URL}/chats/?conversation_id={conversation.id}",
            'item_url': f"{settings.SITE_URL}/categories/{item.category.slug}/",
            'current_year': datetime.now().year,
        }
        
        # Render email content
        subject = f"Someone is interested in your item: {item.title}"
        html_message = render_to_string('accounts/item_request_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[item_owner.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Create notification record
        from .models import Notification
        Notification.objects.create(
            user=item_owner,
            type='post_interest',
            title=f"Interest in your item: {item.title}",
            message=f"{requester.first_name or requester.username} is interested in your item",
            related_post=item
        )
        
        logger.info(f"Item request notification sent to {item_owner.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send item request notification: {str(e)}")
        return False

def send_request_response_notification(request, responder, request_owner, message=None):
    """
    Send email notification to request owner when someone responds to their request
    """
    try:
        # Create conversation for chat
        from .models import Conversation
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=responder
        ).filter(
            participants=request_owner
        ).filter(
            request=request
        ).first()
        
        if not existing_conversation:
            # Create new conversation
            conversation = Conversation.objects.create(request=request)
            conversation.participants.add(responder, request_owner)
        else:
            conversation = existing_conversation
        
        # Prepare email context
        context = {
            'request': request,
            'request_owner': request_owner,
            'responder': responder,
            'message': message,
            'chat_url': f"{settings.SITE_URL}/chats/?conversation_id={conversation.id}",
            'request_url': f"{settings.SITE_URL}/categories/{request.category.slug}/",
            'current_year': datetime.now().year,
        }
        
        # Render email content
        subject = f"Response to your request: {request.title}"
        html_message = render_to_string('accounts/request_response_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request_owner.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Create notification record
        from .models import Notification
        Notification.objects.create(
            user=request_owner,
            type='request_response',
            title=f"Response to your request: {request.title}",
            message=f"{responder.first_name or responder.username} responded to your request",
            related_request=request
        )
        
        logger.info(f"Request response notification sent to {request_owner.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send request response notification: {str(e)}")
        return False

def send_message_notification(message, recipient):
    """
    Send email notification when someone receives a new message
    """
    try:
        # Don't send email if user is currently active (optional)
        # This prevents spam when users are actively chatting
        
        sender = message.sender
        conversation = message.conversation
        
        # Get the item/request context
        context_item = None
        context_type = ""
        if conversation.post:
            context_item = conversation.post
            context_type = "item"
        elif conversation.request:
            context_item = conversation.request
            context_type = "request"
        
        # Prepare email context
        context = {
            'message': message,
            'sender': sender,
            'recipient': recipient,
            'conversation': conversation,
            'context_item': context_item,
            'context_type': context_type,
            'chat_url': f"{settings.SITE_URL}/chats/?conversation_id={conversation.id}",
            'current_year': datetime.now().year,
        }
        
        # Render email content
        subject = f"New message from {sender.first_name or sender.username}"
        if context_item:
            subject += f" - {context_item.title}"
        
        # Use a simple template for messages
        html_message = render_to_string('accounts/chat_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=True,  # Don't fail silently for message notifications
        )
        
        logger.info(f"Message notification sent to {recipient.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send message notification: {str(e)}")
        return False