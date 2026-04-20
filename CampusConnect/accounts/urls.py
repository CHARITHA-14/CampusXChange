from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('', views.home, name='home'),          # Homepage
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),     # Login page
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
    path('homepage/', views.homepage, name='homepage'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category>/', views.category_detail, name='category_detail'),
    path('chats/', views.chats, name='chats'),
    path('logout/', views.logout_view, name='logout'),
    path('old-requests/', views.old_requests, name='old_requests'),
    path('create-post/', views.create_post, name='create_post'),
    path('create-request/', views.create_request, name='create_request'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete-request/<int:request_id>/', views.delete_request, name='delete_request'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Chat API endpoints
    path('api/conversations/', views.conversations_list, name='conversations_list'),
    path('api/conversations/<int:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('api/conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('api/conversations/<int:conversation_id>/send-enhanced/', views.send_message_enhanced, name='send_message_enhanced'),
    path('api/start-conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
    
    # Email notification endpoints
    path('api/express-interest/<int:item_id>/', views.express_interest, name='express_interest'),
    path('api/respond-to-request/<int:request_id>/', views.respond_to_request, name='respond_to_request'),
]
