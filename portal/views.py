import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.files.storage import default_storage
import os

from .models import (
    UserProfile, StoryMaker, Project, Initiative,
    Nomination, ChatMessage, BreakingNews, UploadedFile, Podcast, Service, Investor
)

# ===== MAIN PAGES =====

def home(request):
    # Fetch data for Home
    stories = StoryMaker.objects.all()[:3]
    verified_projects = Project.objects.filter(status='verified')[:3]
    initiatives = Initiative.objects.all()[:3]
    news = BreakingNews.objects.all().order_by('-date')[:15]
    
    # Statistics
    stats = {
        'makers': StoryMaker.objects.count(),
        'projects': Project.objects.filter(status='verified').count(),
        'initiatives': Initiative.objects.count(),
        'users': User.objects.count(),
    }
    
    context = {
        'stories': stories,
        'projects': verified_projects,
        'initiatives': initiatives,
        'news': [n.content for n in news],
        'stats': stats,
    }
    return render(request, 'portal/home.html', context)

def story_list(request):
    stories = StoryMaker.objects.all()
    context = {'stories': stories}
    return render(request, 'portal/story_list.html', context)

def projects_list(request):
    category = request.GET.get('category', '')
    p_type = request.GET.get('type', 'all')
    
    projects_qs = Project.objects.filter(status='verified')
    initiatives_qs = Initiative.objects.filter(status='verified')
    
    if category:
        projects_qs = projects_qs.filter(category=category)
    
    context = {
        'projects': projects_qs if p_type in ('all', 'project') else [],
        'initiatives': initiatives_qs if p_type in ('all', 'initiative') else [],
        'selected_category': category,
        'selected_type': p_type,
    }
    return render(request, 'portal/projects_list.html', context)

def about(request):
    team = ['أحمد علي', 'منى سعيد', 'محمد جلال', 'فاطمة الزهراء', 'خالد عبدالله', 'نورهان أحمد', 'عمر حسن', 'سارة محمود', 'أحمد سامي', 'إسراء محمد', 'محمود علي', 'أسماء محمود', 'يوسف أحمد', 'رقية مصطفى']
    context = {'team': team}
    return render(request, 'portal/about.html', context)

def nominate(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        nom_type = request.POST.get('type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if name and nom_type and description:
            Nomination.objects.create(
                name=name,
                type=nom_type,
                title=title,
                description=description
            )
            messages.success(request, 'تم إرسال الترشيح للمراجعة بنجاح!')
            return redirect('nominate')
        else:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة.')
            
    return render(request, 'portal/nominate.html')

# ===== AUTHENTICATION =====

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            # If not authenticated directly, try all users sharing this email
            matching_users = User.objects.filter(email=email)
            for u in matching_users:
                authenticated_user = authenticate(request, username=u.username, password=password)
                if authenticated_user is not None:
                    user = authenticated_user
                    break
                    
        if user is not None:
            profile = user.profile
            if profile.user_type == 'investor' and profile.status == 'pending':
                messages.error(request, 'حسابك لا يزال قيد المراجعة.')
            else:
                login(request, user)
                messages.success(request, f'مرحباً بك، {profile.user.first_name or profile.user.username}!')
                if profile.user_type == 'admin':
                    return redirect('dashboard')
                return redirect('home')
        else:
            messages.error(request, 'بيانات الدخول غير صحيحة.')
            
    return redirect('home')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('type')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not name or not email or not password:
            messages.error(request, 'الرجاء ملء جميع الحقول الأساسية.')
            return redirect('home')
            
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم بالفعل.')
            return redirect('home')
            
        # Create standard user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()
        
        profile = user.profile
        profile.user_type = user_type
        
        if user_type == 'innovator':
            profile.innovator_type = request.POST.get('innovator_type')
            profile.field = request.POST.get('field')
            profile.status = 'active'
        elif user_type == 'investor':
            profile.company = request.POST.get('company')
            profile.investor_type = request.POST.get('investor_type')
            profile.investment_field = request.POST.get('investment_field')
            profile.status = 'pending'  # Needs admin approval
            
        profile.save()
        
        if user_type == 'investor':
            messages.info(request, 'تم إرسال طلب التسجيل! سيتم تفعيل الحساب بعد المراجعة.')
        else:
            login(request, user)
            messages.success(request, f'تم التسجيل بنجاح! مرحباً بك {name}.')
            
    return redirect('home')

def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('home')

# ===== USER DASHBOARDS =====

@login_required
def dashboard(request):
    profile = request.user.profile
    
    if profile.user_type == 'admin':
        # Admin Dashboard Data
        users_list = UserProfile.objects.exclude(user=request.user)
        projects_list = Project.objects.all()
        storymakers = StoryMaker.objects.all()
        initiatives = Initiative.objects.all()
        nominations = Nomination.objects.all().order_by('-date')
        files = UploadedFile.objects.all().order_by('-date')
        podcasts = Podcast.objects.all().order_by('-date')
        all_services = Service.objects.all().order_by('-date')
        all_investors = Investor.objects.all().order_by('-date')
        
        context = {
            'profile': profile,
            'users_list': users_list,
            'projects_list': projects_list,
            'storymakers': storymakers,
            'initiatives': initiatives,
            'nominations': nominations,
            'files': files,
            'podcasts': podcasts,
            'all_services': all_services,
            'all_investors': all_investors,
        }
        return render(request, 'portal/admin_dashboard.html', context)
        
    elif profile.user_type == 'innovator':
        # Innovator Dashboard Data
        my_projects = Project.objects.filter(innovator=request.user)
        my_initiatives = Initiative.objects.filter(innovator=request.user)
        notifications = profile.notifications[::-1]  # Latest first
        
        context = {
            'profile': profile,
            'projects': my_projects,
            'initiatives': my_initiatives,
            'notifications': notifications,
        }
        return render(request, 'portal/innovator_dashboard.html', context)
        
    elif profile.user_type == 'investor':
        # Investor Dashboard Data
        my_support = profile.support_history[::-1]
        
        context = {
            'profile': profile,
            'support_history': my_support,
        }
        return render(request, 'portal/investor_dashboard.html', context)
        
    return redirect('home')

# ===== DETAILS PAGES =====

def story_detail(request, pk):
    maker = get_object_or_404(StoryMaker, pk=pk)
    maker.views += 1
    maker.save()
    context = {'maker': maker}
    return render(request, 'portal/story_detail.html', context)

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.views += 1
    project.save()
    context = {'project': project}
    return render(request, 'portal/project_detail.html', context)

def initiative_detail(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)
    initiative.views += 1
    initiative.save()
    context = {'initiative': initiative}
    return render(request, 'portal/initiative_detail.html', context)

# ===== FILE MANAGER =====

@login_required
@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        name = request.POST.get('file_name')
        file = request.FILES.get('file_upload')
        
        if name and file:
            UploadedFile.objects.create(name=name, file=file)
            return JsonResponse({'status': 'success', 'message': 'تم رفع الملف بنجاح'})
    return JsonResponse({'status': 'error', 'message': 'بيانات غير صالحة'})

def download_file(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    response = HttpResponse(uploaded_file.file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{uploaded_file.name}.pdf"'
    return response

@login_required
@csrf_exempt
def edit_file_name(request, pk):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        uploaded_file = get_object_or_404(UploadedFile, pk=pk)
        if new_name:
            uploaded_file.name = new_name;
            uploaded_file.save()
            return JsonResponse({'status': 'success', 'message': 'تم تعديل الاسم'})
    return JsonResponse({'status': 'error', 'message': 'فشل التحديث'})

@login_required
@csrf_exempt
def delete_file(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    if uploaded_file.file:
        if os.path.exists(uploaded_file.file.path):
            os.remove(uploaded_file.file.path)
    uploaded_file.delete()
    return JsonResponse({'status': 'success', 'message': 'تم حذف الملف'})

# ===== EXPRESS INTEREST =====

@login_required
@csrf_exempt
def express_interest(request):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.user_type != 'investor':
            return JsonResponse({'status': 'error', 'message': 'هذه الميزة للمستثمرين فقط'})
            
        item_type = request.POST.get('type')
        item_id = request.POST.get('id')
        
        item = None
        item_name = ''
        innovator_user = None
        
        if item_type == 'project':
            item = get_object_or_404(Project, pk=item_id)
            item_name = item.title
            innovator_user = item.innovator
            item.interested += 1
            item.save()
        elif item_type == 'initiative':
            item = get_object_or_404(Initiative, pk=item_id)
            item_name = item.title
        elif item_type == 'maker':
            item = get_object_or_404(StoryMaker, pk=item_id)
            item_name = item.name
        elif item_type == 'service':
            item = get_object_or_404(Service, pk=item_id)
            item_name = item.title
            item.interested += 1
            item.save()
        elif item_type == 'investor_item':
            item = get_object_or_404(Investor, pk=item_id)
            item_name = item.title
            item.interested += 1
            item.save()
            
        if not item:
            return JsonResponse({'status': 'error', 'message': 'العنصر غير موجود'})
            
        msg = f'أبدى المستثمر {request.user.first_name or request.user.username} اهتمامه بدعم {item_type == "maker" and "النموذج" or item_type == "project" and "المشروع" or item_type == "service" and "الخدمة" or item_type == "investor_item" and "المستثمر" or "المبادرة"} "{item_name}"'
        
        # Save to support requests JSON lists directly for tracking on dashboard
        support_request = {
            'investorId': request.user.id,
            'investorName': request.user.first_name or request.user.username,
            'itemType': item_type,
            'itemId': item_id,
            'itemName': item_name,
            'message': msg,
        }
        
        # Save to investor's support history
        profile.support_history.append(support_request)
        profile.save()
        
        # Send Notification to innovator
        if innovator_user:
            innovator_profile = innovator_user.profile
            innovator_profile.notifications.append(msg)
            innovator_profile.save()
            
        # Create BreakingNews
        BreakingNews.objects.create(content=msg)
        
        return JsonResponse({'status': 'success', 'message': 'تم إرسال اهتمامك، وسيتم إشعار صاحب العمل والإدارة'})
        
    return JsonResponse({'status': 'error', 'message': 'طريقة طلب غير صالحة'})

# ===== DIRECT CHATS =====

@login_required
@csrf_exempt
def open_chat(request):
    item_type = request.POST.get('itemType')
    item_id = request.POST.get('itemId')
    other_user_id = request.POST.get('otherUserId')
    
    other_user = None
    item_title = ''
    
    if other_user_id:
        other_user = get_object_or_404(User, pk=other_user_id)
        
    if item_type == 'project':
        item = get_object_or_404(Project, pk=item_id)
        item_title = item.title
        if not other_user:
            other_user = item.innovator
    elif item_type == 'initiative':
        item = get_object_or_404(Initiative, pk=item_id)
        item_title = item.title
    elif item_type == 'maker':
        item = get_object_or_404(StoryMaker, pk=item_id)
        item_title = item.name
    elif item_type == 'service':
        item = get_object_or_404(Service, pk=item_id)
        item_title = item.title
    elif item_type == 'investor_item':
        item = get_object_or_404(Investor, pk=item_id)
        item_title = item.title
        
    # Generate unique conversation identity key
    # Sort IDs so order doesn't matter
    participants = sorted([request.user.id, other_user.id if other_user else 'admin'])
    chat_id = f"chat_{item_type}_{item_id}_{participants[0]}_{participants[1]}"
    
    return JsonResponse({
        'status': 'success',
        'chat_id': chat_id,
    })

@login_required
def chat_list(request):
    # Find all chat rooms where current user participated
    sent_msgs = ChatMessage.objects.filter(sender=request.user)
    recv_msgs = ChatMessage.objects.filter(receiver=request.user)
    
    all_rooms = {}
    
    def process_msg(msg):
        # We can group messages by sender-receiver and related items
        other = msg.receiver if msg.sender == request.user else msg.sender
        other_name = other.first_name or other.username if other else 'الإدارة'
        
        participants = sorted([request.user.id, other.id if other else 'admin'])
        room_id = f"chat_{msg.related_item_type}_{msg.related_item_id}_{participants[0]}_{participants[1]}"
        
        if room_id not in all_rooms:
            all_rooms[room_id] = {
                'id': room_id,
                'other_user_name': other_name,
                'other_user_id': other.id if other else None,
                'related_title': msg.related_item_title or '',
                'last_message': msg.text or '📎 مرفق',
                'last_time': msg.timestamp,
                'unread': 0
            }
        else:
            if msg.timestamp > all_rooms[room_id]['last_time']:
                all_rooms[room_id]['last_message'] = msg.text or '📎 مرفق'
                all_rooms[room_id]['last_time'] = msg.timestamp
                
        if msg.receiver == request.user and not msg.read:
            all_rooms[room_id]['unread'] += 1
            
    for m in sent_msgs:
        process_msg(m)
    for m in recv_msgs:
        process_msg(m)
        
    sorted_rooms = sorted(all_rooms.values(), key=lambda x: x['last_time'], reverse=True)
    
    # Format time
    for r in sorted_rooms:
        r['last_time'] = r['last_time'].strftime('%H:%M %d/%m')
        
    return JsonResponse({'status': 'success', 'chats': sorted_rooms})

@login_required
def chat_window(request, chat_id):
    # Parse chat_id: chat_type_id_user1_user2
    parts = chat_id.split('_')
    if len(parts) < 5:
        return JsonResponse({'status': 'error', 'message': 'معرف محادثة غير صالح'})
        
    item_type = parts[1]
    item_id = int(parts[2])
    u1_id = parts[3]
    u2_id = parts[4]
    
    other_user_id = u2_id if str(request.user.id) == u1_id else u1_id
    other_user = None
    if other_user_id != 'admin':
        other_user = get_object_or_404(User, pk=int(other_user_id))
        
    # Get all messages
    if other_user:
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user),
            related_item_type=item_type,
            related_item_id=item_id
        ).order_by('timestamp')
    else:
        # Chat with admin generally
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver__isnull=True) | Q(sender__isnull=True, receiver=request.user),
            related_item_type=item_type,
            related_item_id=item_id
        ).order_by('timestamp')
        
    # Mark messages as read
    unread = messages.filter(receiver=request.user, read=False)
    unread.update(read=True)
    
    rendered_messages = []
    for msg in messages:
        rendered_messages.append({
            'id': msg.id,
            'senderId': msg.sender.id,
            'senderName': msg.sender.first_name or msg.sender.username,
            'text': msg.text or '',
            'timestamp': msg.timestamp.isoformat(),
            'read': msg.read,
            'attachments': [{
                'url': msg.attachment.url if msg.attachment else '',
                'type': msg.attachment_type,
                'name': msg.attachment_name or 'ملف'
            }] if msg.attachment else []
        })
        
    other_name = other_user.first_name or other_user.username if other_user else 'الإدارة'
    
    return JsonResponse({
        'status': 'success',
        'messages': rendered_messages,
        'other_name': other_name,
        'other_id': other_user.id if other_user else None,
        'current_user_id': request.user.id,
    })

@login_required
@csrf_exempt
def send_message(request, chat_id):
    if request.method == 'POST':
        parts = chat_id.split('_')
        item_type = parts[1]
        item_id = int(parts[2])
        u1_id = parts[3]
        u2_id = parts[4]
        
        other_user_id = u2_id if str(request.user.id) == u1_id else u1_id
        other_user = None
        if other_user_id != 'admin':
            other_user = get_object_or_404(User, pk=int(other_user_id))
            
        text = request.POST.get('text', '').strip()
        attachment = request.FILES.get('attachment')
        attachment_type = request.POST.get('attachment_type', 'none')
        attachment_name = request.POST.get('attachment_name', '')
        
        # Load related item title
        related_title = ''
        if item_type == 'project':
            item = Project.objects.filter(pk=item_id).first()
            related_title = item.title if item else ''
        elif item_type == 'initiative':
            item = Initiative.objects.filter(pk=item_id).first()
            related_title = item.title if item else ''
        elif item_type == 'maker':
            item = StoryMaker.objects.filter(pk=item_id).first()
            related_title = item.name if item else ''
        elif item_type == 'service':
            item = Service.objects.filter(pk=item_id).first()
            related_title = item.title if item else ''
        elif item_type == 'investor_item':
            item = Investor.objects.filter(pk=item_id).first()
            related_title = item.title if item else ''
            
        if not text and not attachment:
            return JsonResponse({'status': 'error', 'message': 'الرسالة فارغة'})
            
        msg = ChatMessage.objects.create(
            sender=request.user,
            receiver=other_user,
            related_item_type=item_type,
            related_item_id=item_id,
            related_item_title=related_title,
            text=text,
            attachment=attachment,
            attachment_type=attachment_type,
            attachment_name=attachment_name
        )
        
        return JsonResponse({'status': 'success', 'message': 'تم إرسال الرسالة'})
        
    return JsonResponse({'status': 'error', 'message': 'طريقة غير صالحة'})

# ===== ADMIN ACTIONS =====

@login_required
@csrf_exempt
def admin_approve_investor(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    investor_profile = get_object_or_404(UserProfile, pk=pk)
    investor_profile.status = 'active'
    investor_profile.save()
    messages.success(request, 'تم تفعيل حساب المستثمر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_user(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    user_profile = get_object_or_404(UserProfile, pk=pk)
    user_obj = user_profile.user
    user_profile.delete()
    user_obj.delete()
    messages.success(request, 'تم حذف المستخدم بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_approve_project(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    project = get_object_or_404(Project, pk=pk)
    project.status = 'verified'
    project.save()
    messages.success(request, 'تم توثيق المشروع بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_project(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'تم حذف المشروع بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_project(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.innovator_name = request.POST.get('innovator_name', project.innovator_name)
        project.faculty = request.POST.get('faculty', project.faculty)
        project.description = request.POST.get('description')
        project.category = request.POST.get('category')
        project.image = request.POST.get('image')
        project.cover_image = request.POST.get('cover_image')
        project.video = request.POST.get('video')
        project.ip_status = request.POST.get('ip_status')
        project.news_content = request.POST.get('news_content')
        project.save()
        messages.success(request, 'تم تحديث المشروع بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_initiative(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    initiative = get_object_or_404(Initiative, pk=pk)
    if request.method == 'POST':
        initiative.title = request.POST.get('title')
        initiative.founder = request.POST.get('founder')
        initiative.description = request.POST.get('description')
        initiative.category = request.POST.get('category')
        initiative.image = request.POST.get('image')
        initiative.cover_image = request.POST.get('cover_image')
        initiative.video = request.POST.get('video')
        initiative.news_content = request.POST.get('news_content')
        achievements_input = request.POST.get('achievements', '')
        initiative.achievements = [a.strip() for a in achievements_input.split(',') if a.strip()]
        initiative.save()
        messages.success(request, 'تم تحديث المبادرة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_approve_initiative(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    initiative = get_object_or_404(Initiative, pk=pk)
    initiative.status = 'verified'
    initiative.save()
    messages.success(request, 'تم توثيق المبادرة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_initiative(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    initiative = get_object_or_404(Initiative, pk=pk)
    initiative.delete()
    messages.success(request, 'تم حذف المبادرة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_story_maker(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    maker = get_object_or_404(StoryMaker, pk=pk)
    if request.method == 'POST':
        maker.name = request.POST.get('name')
        maker.title = request.POST.get('title')
        maker.description = request.POST.get('description')
        maker.video = request.POST.get('video')
        maker.image = request.POST.get('image')
        maker.cover_image = request.POST.get('cover_image')
        maker.news_content = request.POST.get('news_content')
        maker.category = request.POST.get('category')
        maker.save()
        messages.success(request, 'تم تحديث صانع الأثر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_approve_story_maker(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    maker = get_object_or_404(StoryMaker, pk=pk)
    maker.status = 'verified'
    maker.save()
    messages.success(request, 'تم توثيق صانع الأثر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_story_maker(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    maker = get_object_or_404(StoryMaker, pk=pk)
    maker.delete()
    messages.success(request, 'تم حذف صانع الأثر بنجاح.')
    return redirect('dashboard')

@login_required
def admin_nomination_details(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    nomination = get_object_or_404(Nomination, pk=pk)
    context = {'nom': nomination}
    return render(request, 'portal/admin_nomination_detail.html', context)

@login_required
@csrf_exempt
def admin_approve_nomination(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    nom = get_object_or_404(Nomination, pk=pk)
    nom.status = 'approved'
    nom.save()
    messages.success(request, 'تم قبول الترشيح بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_reject_nomination(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    nom = get_object_or_404(Nomination, pk=pk)
    nom.delete()
    messages.success(request, 'تم رفض وحذف الترشيح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_save_from_nomination(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    nom = get_object_or_404(Nomination, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.POST.get('video')
        
        if nom.type == 'project':
            innovator_name = request.POST.get('innovator')
            faculty = request.POST.get('faculty', 'غير محدد')
            category = request.POST.get('category', 'عام')
            
            Project.objects.create(
                title=title,
                innovator_name=innovator_name,
                faculty=faculty,
                category=category,
                description=description,
                video=video,
                image=f"https://via.placeholder.com/400x300/3b82f6/ffffff?text={title}",
                status='verified'
            )
        elif nom.type == 'initiative':
            founder = request.POST.get('founder')
            
            Initiative.objects.create(
                title=title,
                founder=founder,
                description=description,
                video=video,
                image=f"https://via.placeholder.com/400x300/e2e8f0/000000?text={title}",
            )
        elif nom.type == 'innovator':
            name = request.POST.get('name')
            
            StoryMaker.objects.create(
                name=name,
                title=title,
                description=description,
                video=video,
                image=f"https://via.placeholder.com/400x300/3b82f6/ffffff?text={name}",
            )
            
        nom.status = 'added'
        nom.save()
        messages.success(request, 'تم إضافة الترشيح إلى المحتوى العام بنجاح!')
        
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_add_project(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        innovator_name = request.POST.get('innovator')
        faculty = request.POST.get('faculty')
        category = request.POST.get('category')
        description = request.POST.get('description')
        video = request.POST.get('video')
        image = request.POST.get('image')
        cover_image = request.POST.get('cover_image')
        news_content = request.POST.get('news_content')
        
        if title and innovator_name and description:
            Project.objects.create(
                title=title,
                innovator_name=innovator_name,
                faculty=faculty or 'غير محدد',
                category=category or 'عام',
                description=description,
                video=video,
                image=image or f"https://via.placeholder.com/400x300/3b82f6/ffffff?text={title}",
                cover_image=cover_image or None,
                news_content=news_content or None,
                status='verified'
            )
            messages.success(request, 'تم إضافة المشروع بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_add_initiative(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        founder = request.POST.get('founder')
        description = request.POST.get('description')
        video = request.POST.get('video')
        image = request.POST.get('image')
        cover_image = request.POST.get('cover_image')
        news_content = request.POST.get('news_content')
        category = request.POST.get('category')
        
        if title and founder and description:
            Initiative.objects.create(
                title=title,
                founder=founder,
                description=description,
                video=video,
                image=image or f"https://via.placeholder.com/400x300/e2e8f0/000000?text={title}",
                cover_image=cover_image or None,
                news_content=news_content or None,
                category=category or 'عام',
                status='verified'
            )
            messages.success(request, 'تم إضافة المبادرة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_add_maker(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name')
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.POST.get('video')
        image = request.POST.get('image')
        cover_image = request.POST.get('cover_image')
        news_content = request.POST.get('news_content')
        category = request.POST.get('category')
        
        if name and title and description:
            StoryMaker.objects.create(
                name=name,
                title=title,
                description=description,
                video=video,
                image=image or f"https://via.placeholder.com/400x300/3b82f6/ffffff?text={name}",
                cover_image=cover_image or None,
                news_content=news_content or None,
                category=category or 'عام',
                status='verified'
            )
            messages.success(request, 'تم إضافة صانع الأثر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_clear_all_data(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
        
    # Delete database data except the current user/profile
    UserProfile.objects.exclude(user=request.user).delete()
    User.objects.exclude(pk=request.user.pk).delete()
    
    Project.objects.all().delete()
    Initiative.objects.all().delete()
    StoryMaker.objects.all().delete()
    Nomination.objects.all().delete()
    ChatMessage.objects.all().delete()
    BreakingNews.objects.all().delete()
    UploadedFile.objects.all().delete()
    
    messages.success(request, 'تم تفريغ كافة البيانات بنجاح.')
    return redirect('dashboard')

@login_required
def admin_export_data(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
        
    data = {
        'users': [{'username': u.username, 'email': u.email, 'type': u.profile.user_type} for u in User.objects.all()],
        'projects': [{'title': p.title, 'description': p.description, 'innovator': p.innovator_name} for p in Project.objects.all()],
        'storyMakers': [{'name': m.name, 'title': m.title, 'description': m.description} for m in StoryMaker.objects.all()],
        'initiatives': [{'title': i.title, 'founder': i.founder, 'description': i.description} for i in Initiative.objects.all()],
    }
    
    response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="basma-qena-backup.json"'
    return response

# ===== INNOVATOR ACTIONS =====

@login_required
@csrf_exempt
def innovator_add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        type_choice = request.POST.get('type')
        ip_status = request.POST.get('ip_status')
        video = request.POST.get('video')
        cover_image = request.POST.get('cover')
        
        # Get lists from form
        team_members = request.POST.getlist('team[]')
        gallery_images = request.POST.getlist('gallery[]')
        
        if not title or not description or not type_choice or not ip_status:
            return JsonResponse({'status': 'error', 'message': 'الرجاء ملء جميع الحقول المطلوبة'})
            
        if not team_members:
            return JsonResponse({'status': 'error', 'message': 'الرجاء إضافة عضو فريق واحد على الأقل'})
            
        if not gallery_images:
            return JsonResponse({'status': 'error', 'message': 'الرجاء إضافة صورة واحدة على الأقل للمعرض'})
            
        if type_choice == 'project':
            Project.objects.create(
                title=title,
                innovator_name=request.user.first_name or request.user.username,
                innovator=request.user,
                faculty=request.user.profile.field or 'غير محدد',
                category='عام',
                image=cover_image or f"https://via.placeholder.com/400x300/3b82f6/ffffff?text={title}",
                cover_image=cover_image or f"https://via.placeholder.com/800x400/3b82f6/ffffff?text={title}",
                video=video,
                team=team_members,
                images=gallery_images,
                status='pending',
                ip_status=ip_status
            )
        else:
            Initiative.objects.create(
                title=title,
                founder=request.user.first_name or request.user.username,
                innovator=request.user,
                description=description,
                video=video,
                image=cover_image or f"https://via.placeholder.com/400x300/e2e8f0/000000?text={title}",
                cover_image=cover_image or f"https://via.placeholder.com/800x400/e2e8f0/000000?text={title}",
                team=team_members,
                images=gallery_images,
                ip_status=ip_status,
                status='pending',
                achievements=['قيد التحديث']
            )
            
        # Add breaking news notify admin
        BreakingNews.objects.create(content=f'📦 مشروع جديد بانتظار المراجعة: {title}')
        
        return JsonResponse({'status': 'success', 'message': 'تم إضافة المشروع بنجاح! بانتظار مراجعة الإدارة'})
        
    return JsonResponse({'status': 'error', 'message': 'طريقة غير صالحة'})


# ===== PODCAST VIEWS =====

def podcast_list(request):
    podcasts = Podcast.objects.all().order_by('-date')
    context = {'podcasts': podcasts}
    return render(request, 'portal/podcast_list.html', context)

@login_required
@csrf_exempt
def admin_add_podcast(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.POST.get('video')
        audio = request.POST.get('audio')
        audio_file = request.FILES.get('audio_file')
        
        if title and description:
            Podcast.objects.create(
                title=title,
                description=description,
                video=video or None,
                audio=audio or None,
                audio_file=audio_file or None
            )
            messages.success(request, 'تم إضافة البودكاست بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_podcast(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    podcast = get_object_or_404(Podcast, pk=pk)
    if request.method == 'POST':
        podcast.title = request.POST.get('title')
        podcast.description = request.POST.get('description')
        podcast.video = request.POST.get('video')
        podcast.audio = request.POST.get('audio')
        if request.FILES.get('audio_file'):
            podcast.audio_file = request.FILES.get('audio_file')
        podcast.save()
        messages.success(request, 'تم تحديث البودكاست بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_podcast(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    podcast = get_object_or_404(Podcast, pk=pk)
    if podcast.audio_file:
        try:
            if os.path.exists(podcast.audio_file.path):
                os.remove(podcast.audio_file.path)
        except Exception:
            pass
    podcast.delete()
    messages.success(request, 'تم حذف البودكاست بنجاح.')
    return redirect('dashboard')

# ===== SERVICE VIEWS =====

def service_list(request):
    services = Service.objects.all().order_by('-date')
    context = {'services': services}
    return render(request, 'portal/service_list.html', context)

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.views += 1
    service.save()
    context = {'service': service}
    return render(request, 'portal/service_detail.html', context)

@login_required
@csrf_exempt
def admin_add_service(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.POST.get('video')
        image = request.POST.get('image')
        
        if title and description:
            Service.objects.create(
                title=title,
                description=description,
                video=video or None,
                image=image or None
            )
            messages.success(request, 'تم إضافة الخدمة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_service(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        service.video = request.POST.get('video')
        service.image = request.POST.get('image')
        service.save()
        messages.success(request, 'تم تحديث الخدمة بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_service(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    messages.success(request, 'تم حذف الخدمة بنجاح.')
    return redirect('dashboard')

# ===== INVESTOR VIEWS =====

def investor_list(request):
    investors = Investor.objects.all().order_by('-date')
    context = {'investors': investors}
    return render(request, 'portal/investor_list.html', context)

def investor_detail(request, pk):
    investor = get_object_or_404(Investor, pk=pk)
    investor.views += 1
    investor.save()
    context = {'investor': investor}
    return render(request, 'portal/investor_detail.html', context)

@login_required
@csrf_exempt
def admin_add_investor(request):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.POST.get('video')
        image = request.POST.get('image')
        
        if title and description:
            Investor.objects.create(
                title=title,
                description=description,
                video=video or None,
                image=image or None
            )
            messages.success(request, 'تم إضافة المستثمر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_edit_investor(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    investor = get_object_or_404(Investor, pk=pk)
    if request.method == 'POST':
        investor.title = request.POST.get('title')
        investor.description = request.POST.get('description')
        investor.video = request.POST.get('video')
        investor.image = request.POST.get('image')
        investor.save()
        messages.success(request, 'تم تحديث بيانات المستثمر بنجاح.')
    return redirect('dashboard')

@login_required
@csrf_exempt
def admin_delete_investor(request, pk):
    if not request.user.profile.user_type == 'admin':
        return redirect('home')
    investor = get_object_or_404(Investor, pk=pk)
    investor.delete()
    messages.success(request, 'تم حذف المستثمر بنجاح.')
    return redirect('dashboard')
    