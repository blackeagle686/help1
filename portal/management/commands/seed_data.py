from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import UserProfile, StoryMaker, Project, Initiative, BreakingNews

class Command(BaseCommand):
    help = "Seeds initial database records from index.html"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        # 1. Create Users & Profiles
        # Admin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            email="admin@qena.gov.eg"
        )
        if created or not admin_user.password:
            admin_user.set_password("123456")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        admin_profile = admin_user.profile
        admin_profile.user_type = "admin"
        admin_profile.status = "active"
        admin_profile.save()

        # Innovator
        innovator_user, created = User.objects.get_or_create(
            username="amr",
            email="amr@test.com"
        )
        if created or not innovator_user.password:
            innovator_user.set_password("123456")
            innovator_user.save()
        innovator_profile = innovator_user.profile
        innovator_profile.user_type = "innovator"
        innovator_profile.status = "active"
        innovator_profile.field = "هندسة"
        innovator_profile.innovator_type = "student"
        innovator_profile.save()

        # Investor
        investor_user, created = User.objects.get_or_create(
            username="ahmed",
            email="ahmed@test.com"
        )
        if created or not investor_user.password:
            investor_user.set_password("123456")
            investor_user.save()
        investor_profile = investor_user.profile
        investor_profile.user_type = "investor"
        investor_profile.status = "active"
        investor_profile.company = "شركة النور"
        investor_profile.investor_type = "company"
        investor_profile.save()

        self.stdout.write(self.style.SUCCESS("Users created/verified."))

        # 2. Seed Breaking News
        breaking_items = [
            'محافظ قنا يعلن دعمه الكامل للمبتكرين من أبناء المحافظة',
            'رئيس جامعة جنوب الوادي يوجه بدعم مشروعات التخرج المبتكرة',
            'طلاب هندسة قنا يفوزون بالمركز الأول في مسابقة الابتكار',
            'البنك الأهلي يعلن دعم رواد الأعمال في قنا',
            'افتتاح أول حاضنة أعمال جامعية في صعيد مصر'
        ]
        for content in breaking_items:
            BreakingNews.objects.get_or_create(content=content)
        self.stdout.write(self.style.SUCCESS("Breaking news seeded."))

        # 3. Seed StoryMakers
        story_makers_data = [
            {
                'name': 'اللواء أشرف الداودي',
                'title': 'محافظ قنا',
                'image': 'https://www.qena.gov.eg/wp-content/uploads/2023/10/governor.jpg',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'محافظ قنا، قائد مسيرة التنمية بالمحافظة',
                'full_story': 'اللواء أشرف الداودي تولى منصب محافظ قنا في...',
                'achievements': ['افتتاح 120 مشروع تنموي', 'دعم 500 مبتكر'],
                'news': ['المحافظ يلتقي شباب المبتكرين', 'إطلاق مبادرة دعم المشروعات الصغيرة']
            },
            {
                'name': 'أ.د. أحمد عكاوي',
                'title': 'رئيس جامعة جنوب الوادي',
                'image': 'https://www.swu.edu.eg/wp-content/uploads/2023/08/president.jpg',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'رئيس الجامعة، يدعم البحث العلمي والابتكار',
                'full_story': 'الأستاذ الدكتور أحمد عكاوي رئيس جامعة جنوب الوادي...',
                'achievements': [],
                'news': []
            },
            {
                'name': 'د. محمود خضاري',
                'title': 'نائب محافظ قنا',
                'image': 'https://www.qena.gov.eg/wp-content/uploads/2023/10/deputy.jpg',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'نائب محافظ قنا',
                'full_story': '',
                'achievements': [],
                'news': []
            },
            {
                'name': 'أ.د. بدوي شحات',
                'title': 'نائب رئيس الجامعة',
                'image': 'https://www.swu.edu.eg/wp-content/uploads/2023/08/vp.jpg',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'نائب رئيس الجامعة',
                'full_story': '',
                'achievements': [],
                'news': []
            },
            {
                'name': 'أ.د. محمد سعيد',
                'title': 'عميد كلية الهندسة',
                'image': 'https://eng.svu.edu.eg/wp-content/uploads/2023/09/dean.jpg',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'عميد كلية الهندسة',
                'full_story': '',
                'achievements': [],
                'news': []
            },
            {
                'name': 'م. عمرو خالد',
                'title': 'طالب مبتكر - كلية الهندسة',
                'image': 'https://via.placeholder.com/400x300/1A4D3E/ffffff?text=عمرو+خالد',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'طالب مبتكر بكلية الهندسة بجامعة جنوب الوادي',
                'full_story': '',
                'achievements': [],
                'news': []
            }
        ]
        for data in story_makers_data:
            StoryMaker.objects.get_or_create(
                name=data['name'],
                defaults={
                    'title': data['title'],
                    'image': data['image'],
                    'video': data['video'],
                    'description': data['description'],
                    'full_story': data['full_story'],
                    'achievements': data['achievements'],
                    'news': data['news']
                }
            )
        self.stdout.write(self.style.SUCCESS("Story makers seeded."))

        # 4. Seed Projects
        projects_data = [
            {
                'title': 'نظام الري الذكي بالطاقة الشمسية',
                'innovator_name': 'م. عمرو خالد',
                'innovator': innovator_user,
                'faculty': 'كلية الهندسة',
                'category': 'زراعة',
                'image': 'https://via.placeholder.com/400x300/1A4D3E/ffffff?text=نظام+الري+الذكي',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'نظام مبتكر لري الأراضي الزراعية باستخدام الطاقة الشمسية، يوفر 70% من استهلاك المياه.',
                'team': ['عمرو خالد', 'د. أحمد علي'],
                'images': [
                    'https://via.placeholder.com/800x600/1A4D3E/ffffff?text=صورة+1',
                    'https://via.placeholder.com/800x600/F97316/ffffff?text=صورة+2'
                ],
                'status': 'verified',
                'ip_status': 'registered',
            },
            {
                'title': 'تطبيق حورس للخدمات الحكومية',
                'innovator_name': 'أحمد علي',
                'innovator': None,
                'faculty': 'كلية الحاسبات',
                'category': 'تكنولوجيا',
                'image': 'https://via.placeholder.com/400x300/F97316/ffffff?text=تطبيق+حورس',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'تطبيق لتقديم الخدمات الحكومية إلكترونياً',
                'team': [],
                'images': [],
                'status': 'pending',
                'ip_status': 'idea',
            },
            {
                'title': 'إعادة تدوير المخلفات الزراعية',
                'innovator_name': 'فاطمة الزهراء',
                'innovator': None,
                'faculty': 'كلية العلوم',
                'category': 'بيئة',
                'image': 'https://via.placeholder.com/400x300/0B3B2C/ffffff?text=تدوير+المخلفات',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'description': 'مشروع لتحويل المخلفات الزراعية إلى منتجات صديقة للبيئة',
                'team': [],
                'images': [],
                'status': 'verified',
                'ip_status': 'registered',
            }
        ]
        for data in projects_data:
            Project.objects.get_or_create(
                title=data['title'],
                defaults={
                    'innovator_name': data['innovator_name'],
                    'innovator': data['innovator'],
                    'faculty': data['faculty'],
                    'category': data['category'],
                    'image': data['image'],
                    'video': data['video'],
                    'description': data['description'],
                    'team': data['team'],
                    'images': data['images'],
                    'status': data['status'],
                    'ip_status': data['ip_status']
                }
            )
        self.stdout.write(self.style.SUCCESS("Projects seeded."))

        # 5. Seed Initiatives
        initiatives_data = [
            {
                'title': 'مبادرة حياة كريمة - قنا',
                'founder': 'محافظة قنا',
                'description': 'مبادرة رئاسية لتطوير الريف المصري، تستهدف 120 قرية في قنا',
                'image': 'https://via.placeholder.com/400x300/1A4D3E/ffffff?text=حياة+كريمة',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'achievements': ['تطوير 50 قرية', 'إنشاء 30 مدرسة']
            },
            {
                'title': 'مبادرة ابدأ',
                'founder': 'جهاز تنمية المشروعات',
                'description': 'دعم المشروعات الصغيرة',
                'image': 'https://via.placeholder.com/400x300/F97316/ffffff?text=ابدأ',
                'video': 'https://youtu.be/gIqYZJzrZyM?si=MiYuR6x7o1Rks1D6',
                'achievements': []
            }
        ]
        for data in initiatives_data:
            Initiative.objects.get_or_create(
                title=data['title'],
                defaults={
                    'founder': data['founder'],
                    'description': data['description'],
                    'image': data['image'],
                    'video': data['video'],
                    'achievements': data['achievements']
                }
            )
        self.stdout.write(self.style.SUCCESS("Initiatives seeded."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
