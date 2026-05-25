from django.test import TestCase, Client
from django.contrib.auth.models import User
from portal.models import Service, UserProfile, Investor, TeamMember, Podcast
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


class TeamMemberTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = TeamMember.objects.create(
            name="عضو تجريبي",
            role="مطور برمجيات",
            image="team/member.jpg"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.user_type = "admin"
        self.admin_profile.save()

    def test_about_view_with_team_members(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "عضو تجريبي")
        self.assertContains(response, "مطور برمجيات")

    def test_about_view_fallback(self):
        TeamMember.objects.all().delete()
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أحمد علي")

    def test_admin_add_team_member(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/gif'
        )
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_add_team_member'), {
            'name': 'عضو جديد',
            'role': 'مصمم واجهات',
            'image': test_image
        })
        self.assertEqual(response.status_code, 302)
        
        new_member = TeamMember.objects.get(name="عضو جديد")
        self.assertEqual(new_member.role, "مصمم واجهات")
        self.assertTrue(new_member.image.name.startswith('team/test_image'))

    def test_admin_edit_team_member(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile(
            name='edited_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/gif'
        )
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_edit_team_member', args=[self.member.pk]), {
            'name': 'اسم معدل',
            'role': 'دور معدل',
            'image': test_image
        })
        self.assertEqual(response.status_code, 302)
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, "اسم معدل")
        self.assertEqual(self.member.role, "دور معدل")
        self.assertTrue(self.member.image.name.startswith('team/edited_image'))

    def test_admin_delete_team_member(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_delete_team_member', args=[self.member.pk]))
        self.assertEqual(response.status_code, 302)
        
        with self.assertRaises(TeamMember.DoesNotExist):
            TeamMember.objects.get(pk=self.member.pk)

    def test_admin_add_team_member_invalid_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        bad_file = SimpleUploadedFile(
            name='script.sh',
            content=b'echo "bad script"',
            content_type='text/x-shellscript'
        )
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_add_team_member'), {
            'name': 'مخترق',
            'role': 'تجسس',
            'image': bad_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TeamMember.objects.filter(name="مخترق").exists())

    def test_admin_add_team_member_oversized(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        huge_file = SimpleUploadedFile(
            name='huge.jpg',
            content=b'\x00' * (3 * 1024 * 1024),
            content_type='image/jpeg'
        )
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(reverse('admin_add_team_member'), {
            'name': 'كبير جدا',
            'role': 'حجم زائد',
            'image': huge_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TeamMember.objects.filter(name="كبير جدا").exists())


class PodcastTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.podcast_youtube = Podcast.objects.create(
            title="بودكاست يوتيوب تجريبي",
            description="وصف بودكاست يوتيوب تجريبي",
            video="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        self.podcast_audio = Podcast.objects.create(
            title="بودكاست صوتي تجريبي",
            description="وصف بودكاست صوتي تجريبي",
            audio="https://drive.google.com/file/d/12345/view?usp=sharing"
        )
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin_podcast",
            email="admin_pod@example.com",
            password="adminpassword"
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.user_type = "admin"
        self.admin_profile.save()

    def test_podcast_list_view(self):
        # Importing Podcast model inside tests to ensure it runs correctly
        from portal.models import Podcast
        response = self.client.get(reverse('podcast_list'))
        self.assertEqual(response.status_code, 200)
        # Verify both podcasts are present (meaning loop skip logic is fixed!)
        self.assertContains(response, "بودكاست يوتيوب تجريبي")
        self.assertContains(response, "بودكاست صوتي تجريبي")

    def test_podcast_detail_view(self):
        response = self.client.get(reverse('podcast_detail', args=[self.podcast_youtube.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بودكاست يوتيوب تجريبي")
        
        # Check that it uses the embed video filter
        self.assertContains(response, "https://www.youtube.com/embed/dQw4w9WgXcQ")

        # Check audio podcast detail view
        response_audio = self.client.get(reverse('podcast_detail', args=[self.podcast_audio.pk]))
        self.assertEqual(response_audio.status_code, 200)
        self.assertContains(response_audio, "بودكاست صوتي تجريبي")
        
        # Check that it converts Google Drive audio link to docs.google.com download URL
        self.assertContains(response_audio, "https://docs.google.com/uc?export=download&amp;id=12345")

    def test_admin_add_podcast_valid_audio(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="admin_podcast", password="adminpassword")
        
        # Valid small MP3 file
        audio_file = SimpleUploadedFile("test.mp3", b"dummy mp3 data", content_type="audio/mpeg")
        
        response = self.client.post(reverse('admin_add_podcast'), {
            'title': 'بودكاست جديد',
            'description': 'وصف بودكاست جديد',
            'audio_file': audio_file
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        # Should be created successfully
        new_podcast = Podcast.objects.get(title="بودكاست جديد")
        self.assertIsNotNone(new_podcast.audio_file)

    def test_admin_add_podcast_invalid_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="admin_podcast", password="adminpassword")
        
        # Invalid TXT extension
        audio_file = SimpleUploadedFile("test.txt", b"dummy txt data", content_type="text/plain")
        
        response = self.client.post(reverse('admin_add_podcast'), {
            'title': 'بودكاست غير صالح',
            'description': 'وصف بودكاست غير صالح',
            'audio_file': audio_file
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        # Should NOT be created
        with self.assertRaises(Podcast.DoesNotExist):
            Podcast.objects.get(title="بودكاست غير صالح")

    def test_admin_add_podcast_too_large(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username="admin_podcast", password="adminpassword")
        
        # File larger than 5MB
        large_data = b"0" * (5 * 1024 * 1024 + 1)
        audio_file = SimpleUploadedFile("large_test.mp3", large_data, content_type="audio/mpeg")
        
        response = self.client.post(reverse('admin_add_podcast'), {
            'title': 'بودكاست ضخم',
            'description': 'وصف بودكاست ضخم',
            'audio_file': audio_file
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        
        # Should NOT be created
        with self.assertRaises(Podcast.DoesNotExist):
            Podcast.objects.get(title="بودكاست ضخم")
