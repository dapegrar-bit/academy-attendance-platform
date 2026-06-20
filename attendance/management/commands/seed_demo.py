from datetime import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from attendance.models import Batch, TraineeProfile, Session, AttendanceRecord, Announcement, SiteSetting


class Command(BaseCommand):
    help = 'Create demo data for Academy Attendance Platform'

    def handle(self, *args, **options):
        setting = SiteSetting.current()
        setting.academy_name = 'أكاديميتي'
        setting.system_name = 'النظام الشامل للحضور والمحاضرات'
        setting.logo_url = 'https://i.top4top.io/p_3822gqcjp1.png'
        setting.save()

        admin, created = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True, 'first_name': 'إدارة أكاديميتي'})
        admin.is_staff = True
        admin.is_superuser = True
        admin.first_name = 'إدارة أكاديميتي'
        admin.set_password('admin123')
        admin.save()

        batch1, _ = Batch.objects.get_or_create(name='دفعة تطوير الويب - الفوج الأول', defaults={'description': 'برنامج تدريبي عملي على تطوير الويب', 'color': '#2f7d6f'})
        batch2, _ = Batch.objects.get_or_create(name='دفعة تصميم الجرافيك', defaults={'description': 'برنامج تدريبي في التصميم الرقمي', 'color': '#f2bd3a'})

        trainees = [
            ('sara', 'سارة العتيبي', '0511111111', '1234', batch1),
            ('mohammed', 'محمد القحطاني', '0522222222', '1234', batch1),
            ('khaled', 'خالد المالكي', '0533333333', '1234', batch2),
        ]
        for username, full_name, phone, password, batch in trainees:
            user, _ = User.objects.get_or_create(username=username, defaults={'first_name': full_name, 'email': f'{username}@example.com'})
            user.first_name = full_name
            user.set_password(password)
            user.save()
            profile, _ = TraineeProfile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.phone = phone
            profile.batch = batch
            profile.save()

        today = timezone.localdate()
        session, _ = Session.objects.get_or_create(
            batch=batch1,
            title='محاضرة مقدمة في تطوير الواجهات',
            date=today,
            defaults={
                'description': 'محاضرة اليوم الخاصة بالدفعة الأولى',
                'start_time': time(18, 0),
                'end_time': time(20, 0),
                'zoom_url': 'https://zoom.us/j/123456789',
                'is_active': True,
            },
        )
        Session.objects.get_or_create(
            batch=batch1,
            title='تطبيق عملي على لوحات التحكم',
            date=today.replace(day=max(1, today.day - 1)),
            defaults={'zoom_url': 'https://zoom.us/j/987654321', 'start_time': time(18, 0), 'is_active': True},
        )
        sara = TraineeProfile.objects.filter(user__username='sara').first()
        if sara:
            AttendanceRecord.objects.get_or_create(trainee=sara, session=session, defaults={'status': 'present', 'zoom_url_snapshot': session.zoom_url})

        Announcement.objects.get_or_create(title='مرحبًا بكم في أكاديميتي', defaults={'body': 'يرجى الضغط على زر التحضير قبل فتح رابط زووم لضمان تسجيل حضوركم.', 'audience': 'all'})
        self.stdout.write(self.style.SUCCESS('Demo data is ready.'))
