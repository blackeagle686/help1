from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_TYPES = [
        ('admin', 'مدير النظام'),
        ('innovator', 'مبتكر'),
        ('investor', 'مستثمر'),
    ]
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('pending', 'قيد الانتظار'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='innovator')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Innovator Fields
    field = models.CharField(max_length=100, blank=True, null=True)  # الكلية أو التخصص
    innovator_type = models.CharField(max_length=50, blank=True, null=True)  # طالب، باحث، مبتكر حر
    
    # Investor Fields
    company = models.CharField(max_length=100, blank=True, null=True)  # اسم الشركة/الجهة
    investor_type = models.CharField(max_length=50, blank=True, null=True)  # فرد، حاضنة أعمال، شركة، إلخ
    investment_field = models.CharField(max_length=100, blank=True, null=True)  # مجال الاهتمام الاستثماري
    
    # Notifications and history
    notifications = models.JSONField(default=list, blank=True)
    support_history = models.JSONField(default=list, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()


class StoryMaker(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    image = models.URLField(max_length=500, blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField()
    full_story = models.TextField(blank=True, null=True)
    achievements = models.JSONField(default=list, blank=True)
    news = models.JSONField(default=list, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('verified', 'موثق'),
    ]
    
    title = models.CharField(max_length=200)
    innovator_name = models.CharField(max_length=150)  # اسم المبتكر (نص للتوافق)
    innovator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', blank=True, null=True)
    faculty = models.CharField(max_length=100, default='غير محدد')
    category = models.CharField(max_length=50, default='عام')
    image = models.URLField(max_length=500, blank=True, null=True)
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField()
    team = models.JSONField(default=list, blank=True)  # قائمة أسماء الفريق
    images = models.JSONField(default=list, blank=True)  # قائمة روابط معرض الصور
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    views = models.PositiveIntegerField(default=0)
    interested = models.PositiveIntegerField(default=0)
    ip_status = models.CharField(max_length=50, default='idea')  # فكرة، مسجلة، قيد التسجيل
    news_content = models.TextField(blank=True, null=True)  # أخبار ومستجدات المشروع
    date = models.DateField(auto_now_add=True)
    support_requests = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.title


class Initiative(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('verified', 'موثق'),
    ]

    title = models.CharField(max_length=200)
    founder = models.CharField(max_length=150)  # اسم المؤسس (نص للتوافق)
    innovator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiatives', blank=True, null=True)
    category = models.CharField(max_length=50, default='عام')
    image = models.URLField(max_length=500, blank=True, null=True)
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField()
    team = models.JSONField(default=list, blank=True)  # قائمة أسماء الفريق
    images = models.JSONField(default=list, blank=True)  # قائمة روابط معرض الصور
    achievements = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    views = models.PositiveIntegerField(default=0)
    interested = models.PositiveIntegerField(default=0)
    ip_status = models.CharField(max_length=50, default='idea')  # فكرة، مسجلة، قيد التسجيل
    news_content = models.TextField(blank=True, null=True)  # أخبار ومستجدات المبادرة
    date = models.DateField(auto_now_add=True)
    support_requests = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title


class Nomination(models.Model):
    TYPE_CHOICES = [
        ('innovator', '💡 مبتكر'),
        ('initiative', '🤝 مبادرة'),
        ('project', '📋 مشروع'),
        ('university', '🏛️ جامعة'),
    ]
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('added', 'تمت الإضافة'),
    ]
    
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', blank=True, null=True)
    
    # Related items context
    related_item_type = models.CharField(max_length=50, blank=True, null=True)  # project, initiative, maker
    related_item_id = models.IntegerField(blank=True, null=True)
    related_item_title = models.CharField(max_length=200, blank=True, null=True)
    
    text = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    attachment_type = models.CharField(max_length=20, default='none')  # image, video, audio, file
    attachment_name = models.CharField(max_length=200, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"من {self.sender.username} في {self.timestamp}"


class BreakingNews(models.Model):
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


class UploadedFile(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='files/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
