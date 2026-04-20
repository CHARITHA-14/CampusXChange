# CampusConnect Email Notification System

## Overview

The CampusConnect platform now includes a comprehensive email notification system that automatically sends professional emails when users interact with items and requests. This system enhances user engagement and ensures users never miss important interactions.

## Features Implemented

### 1. **Item Interest Notifications** 🎉
- **When**: Someone expresses interest in your posted item
- **Who Gets Notified**: The item owner
- **What's Included**:
  - Beautifully designed email with item details
  - Information about the interested person
  - Optional message from the interested user
  - Direct links to start a conversation
  - Safety reminders for transactions

### 2. **Request Response Notifications** 🎯
- **When**: Someone responds to your item request
- **Who Gets Notified**: The request owner
- **What's Included**:
  - Request details and budget information
  - Responder's profile information and ratings
  - Optional response message
  - Direct links to start conversation
  - Safety guidelines

### 3. **Chat Message Notifications** 💬
- **When**: Someone sends you a message in chat
- **Who Gets Notified**: Message recipient
- **What's Included**:
  - Message preview
  - Context about the item/request being discussed
  - Direct link to continue the conversation

## How It Works

### For Users

#### Expressing Interest in Items:
1. Browse items in any category
2. Click "Express Interest" on items you want
3. Write an optional message to the seller
4. The seller receives an instant email notification
5. Both users can now start chatting through the platform

#### Responding to Requests:
1. View requests from other users
2. Click "Respond to Request" if you can help
3. Write your response message
4. The requester gets an email notification immediately
5. Chat conversation is automatically set up

### For Developers

#### Email Templates:
- `item_request_email.html` - Professional template for item interest notifications
- `request_response_email.html` - Template for request response notifications  
- `chat_email.html` - Template for new message notifications

#### API Endpoints:
- `POST /api/express-interest/<item_id>/` - Express interest in an item
- `POST /api/respond-to-request/<request_id>/` - Respond to a request
- `POST /api/conversations/<id>/send-enhanced/` - Send message with notifications

#### Utility Functions:
- `send_item_request_notification()` - Sends item interest emails
- `send_request_response_notification()` - Sends request response emails  
- `send_message_notification()` - Sends new message emails

## Email Configuration

### Development Setup:
1. **Console Backend** (for testing):
   ```env
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

2. **Gmail SMTP** (for real emails):
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=CampusConnect <noreply@campusxchange.com>
   SITE_URL=http://localhost:8000
   ```

### Gmail App Password Setup:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use your Gmail address for `EMAIL_HOST_USER`
4. Use the App Password for `EMAIL_HOST_PASSWORD`

## Email Templates Design

All email templates feature:
- **Modern Design**: Clean, professional layouts with gradients and shadows
- **Mobile Responsive**: Works perfectly on all devices
- **Brand Consistency**: CampusConnect branding throughout
- **Safety Features**: Built-in safety reminders and guidelines
- **User-Friendly**: Clear call-to-action buttons and easy-to-read content
- **Context Aware**: Shows relevant item/request information

## Safety Features

Every email includes:
- Reminders to meet in safe, public places
- Warnings against sharing sensitive information
- Encouragement to use the platform's chat system
- Guidelines for verifying user identities

## Database Integration

The system automatically:
- Creates conversation records for chat functionality
- Stores notification records in the database
- Links conversations to specific items/requests
- Handles duplicate conversation prevention

## Testing

To test the email system:

1. **Console Backend Testing**:
   - Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
   - Emails will be printed to the console instead of sent

2. **Real Email Testing**:
   - Configure Gmail SMTP settings
   - Create test posts/requests
   - Express interest or respond to test interactions
   - Check email inbox for notifications

## Error Handling

The system includes robust error handling:
- Failed email sends don't break user interactions
- Detailed logging for debugging
- Graceful fallbacks for missing data
- User-friendly error messages

## Performance Considerations

- Email sending is done synchronously but with fail-safe handling
- For high-volume usage, consider implementing async email sending
- Email templates are optimized for fast loading
- Database queries are optimized to prevent N+1 problems

## Future Enhancements

Potential improvements:
- Email preferences/unsubscribe functionality
- Digest emails for multiple notifications
- Real-time push notifications
- Email scheduling for optimal delivery times
- A/B testing for email templates

## Troubleshooting

### Common Issues:

1. **Emails not sending**:
   - Check email backend configuration
   - Verify Gmail app password is correct
   - Check Django logs for error messages

2. **Template rendering errors**:
   - Ensure all template variables are properly passed
   - Check for syntax errors in templates

3. **Chat links not working**:
   - Verify `SITE_URL` setting is correct
   - Check conversation creation logic

### Debug Commands:
```bash
# Test email configuration
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])"

# Check system configuration
python manage.py check

# View email in console (console backend)
python manage.py runserver
# Then trigger notifications and watch console output
```

---

This email notification system significantly enhances the CampusConnect user experience by keeping users informed about important interactions while maintaining the platform's professional appearance and safety standards.
