from django.test import TestCase, Client
from django.contrib.auth.models import User
from portal.models import Service, UserProfile, Investor
from django.urls import reverse

class ServiceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            title="خدمة تجريبية",
            description="وصف خدمة تجريبية",
            image="https://example.com/image.jpg",
            video="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.user_type = "admin"
        self.admin_profile.save()

    def test_services_list_view(self):
        response = self.client.get(reverse('services'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "خدمة تجريبية")

    def test_service_detail_view(self):
        # Service views starts at 0
        self.assertEqual(self.service.views, 0)
        response = self.client.get(reverse('service_detail', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Reload service from DB
        self.service.refresh_from_db()
        self.assertEqual(self.service.views, 1)

    def test_admin_add_service(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_add_service'), {
            'title': 'خدمة جديدة مضافة',
            'description': 'وصف الخدمة الجديدة',
            'image': 'https://example.com/new.jpg'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        new_service = Service.objects.get(title="خدمة جديدة مضافة")
        self.assertEqual(new_service.description, "وصف الخدمة الجديدة")

    def test_admin_edit_service(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_edit_service', args=[self.service.pk]), {
            'title': 'عنوان خدمة معدل',
            'description': 'وصف معدل للخدمة',
            'image': 'https://example.com/edited.jpg'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, "عنوان خدمة معدل")
        self.assertEqual(self.service.description, "وصف معدل للخدمة")

    def test_admin_delete_service(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_delete_service', args=[self.service.pk]))
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        with self.assertRaises(Service.DoesNotExist):
            Service.objects.get(pk=self.service.pk)


class InvestorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.investor = Investor.objects.create(
            title="مستثمر تجريبي",
            description="وصف مستثمر تجريبي",
            image="https://example.com/investor.jpg",
            video="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.user_type = "admin"
        self.admin_profile.save()

    def test_investors_list_view(self):
        response = self.client.get(reverse('investors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مستثمر تجريبي")

    def test_investor_detail_view(self):
        # Investor views starts at 0
        self.assertEqual(self.investor.views, 0)
        response = self.client.get(reverse('investor_detail', args=[self.investor.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Reload investor from DB
        self.investor.refresh_from_db()
        self.assertEqual(self.investor.views, 1)

    def test_admin_add_investor(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_add_investor'), {
            'title': 'مستثمر جديد مضاف',
            'description': 'وصف المستثمر الجديد',
            'image': 'https://example.com/new_investor.jpg'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        new_investor = Investor.objects.get(title="مستثمر جديد مضاف")
        self.assertEqual(new_investor.description, "وصف المستثمر الجديد")

    def test_admin_edit_investor(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_edit_investor', args=[self.investor.pk]), {
            'title': 'عنوان مستثمر معدل',
            'description': 'وصف معدل للمستثمر',
            'image': 'https://example.com/edited_investor.jpg'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        self.investor.refresh_from_db()
        self.assertEqual(self.investor.title, "عنوان مستثمر معدل")
        self.assertEqual(self.investor.description, "وصف معدل للمستثمر")

    def test_admin_delete_investor(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_delete_investor', args=[self.investor.pk]))
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        with self.assertRaises(Investor.DoesNotExist):
            Investor.objects.get(pk=self.investor.pk)
