from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('story/', views.story_list, name='story'),
    path('projects/', views.projects_list, name='projects'),
    path('about/', views.about, name='about'),
    path('nominate/', views.nominate, name='nominate'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Details
    path('story/<int:pk>/', views.story_detail, name='story_detail'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('initiative/<int:pk>/', views.initiative_detail, name='initiative_detail'),
    
    # File Manager
    path('file/upload/', views.upload_file, name='upload_file'),
    path('file/download/<int:pk>/', views.download_file, name='download_file'),
    path('file/edit-name/<int:pk>/', views.edit_file_name, name='edit_file_name'),
    path('file/delete/<int:pk>/', views.delete_file, name='delete_file'),
    
    # Support
    path('express-interest/', views.express_interest, name='express_interest'),
    
    # Chats
    path('chat/open/', views.open_chat, name='open_chat'),
    path('chat/list/', views.chat_list, name='chat_list'),
    path('chat/window/<str:chat_id>/', views.chat_window, name='chat_window'),
    path('chat/send/<str:chat_id>/', views.send_message, name='send_message'),
    
    # Admin Dashboard Actions
    path('admin/approve-investor/<int:pk>/', views.admin_approve_investor, name='admin_approve_investor'),
    path('admin/delete-user/<int:pk>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/approve-project/<int:pk>/', views.admin_approve_project, name='admin_approve_project'),
    path('admin/delete-project/<int:pk>/', views.admin_delete_project, name='admin_delete_project'),
    path('admin/edit-project/<int:pk>/', views.admin_edit_project, name='admin_edit_project'),
    path('admin/edit-initiative/<int:pk>/', views.admin_edit_initiative, name='admin_edit_initiative'),
    path('admin/approve-initiative/<int:pk>/', views.admin_approve_initiative, name='admin_approve_initiative'),
    path('admin/delete-initiative/<int:pk>/', views.admin_delete_initiative, name='admin_delete_initiative'),
    path('admin/edit-story-maker/<int:pk>/', views.admin_edit_story_maker, name='admin_edit_story_maker'),
    path('admin/approve-story-maker/<int:pk>/', views.admin_approve_story_maker, name='admin_approve_story_maker'),
    path('admin/delete-story-maker/<int:pk>/', views.admin_delete_story_maker, name='admin_delete_story_maker'),
    path('admin/nomination-details/<int:pk>/', views.admin_nomination_details, name='admin_nomination_details'),
    path('admin/approve-nomination/<int:pk>/', views.admin_approve_nomination, name='admin_approve_nomination'),
    path('admin/reject-nomination/<int:pk>/', views.admin_reject_nomination, name='admin_reject_nomination'),
    path('admin/save-from-nomination/<int:pk>/', views.admin_save_from_nomination, name='admin_save_from_nomination'),
    path('admin/add-project/', views.admin_add_project, name='admin_add_project'),
    path('admin/add-initiative/', views.admin_add_initiative, name='admin_add_initiative'),
    path('admin/add-maker/', views.admin_add_maker, name='admin_add_maker'),
    path('admin/clear-all-data/', views.admin_clear_all_data, name='admin_clear_all_data'),
    path('admin/export-data/', views.admin_export_data, name='admin_export_data'),
    
    # Podcasts
    path('podcast/', views.podcast_list, name='podcast_list'),
    path('admin/add-podcast/', views.admin_add_podcast, name='admin_add_podcast'),
    path('admin/edit-podcast/<int:pk>/', views.admin_edit_podcast, name='admin_edit_podcast'),
    path('admin/delete-podcast/<int:pk>/', views.admin_delete_podcast, name='admin_delete_podcast'),
    
    # Innovator Actions
    path('innovator/add-project/', views.innovator_add_project, name='innovator_add_project'),
]
