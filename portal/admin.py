from django.contrib import admin
from .models import (
    UserProfile, StoryMaker, Project, Initiative,
    Nomination, ChatMessage, BreakingNews, UploadedFile
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'status', 'join_date')
    list_filter = ('user_type', 'status')
    search_fields = ('user__username', 'user__email', 'company')

@admin.register(StoryMaker)
class StoryMakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'date')
    search_fields = ('name', 'title')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'innovator_name', 'status', 'category', 'date')
    list_filter = ('status', 'category')
    search_fields = ('title', 'innovator_name', 'faculty')

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'founder', 'date')
    search_fields = ('title', 'founder')

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'title', 'status', 'date')
    list_filter = ('type', 'status')
    search_fields = ('name', 'title')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'related_item_type', 'timestamp', 'read')
    list_filter = ('read', 'related_item_type')
    search_fields = ('sender__username', 'receiver__username', 'text')

@admin.register(BreakingNews)
class BreakingNewsAdmin(admin.ModelAdmin):
    list_display = ('content', 'date')
    search_fields = ('content',)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
