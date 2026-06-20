import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import SiteSetting


class Command(BaseCommand):
    help = 'Initialize production platform settings and optional admin user from environment variables.'

    def handle(self, *args, **options):
        setting = SiteSetting.current()
        setting.academy_name = os.environ.get('ACADEMY_NAME', setting.academy_name or 'أكاديميتي')
        setting.system_name = os.environ.get('SYSTEM_NAME', setting.system_name or 'النظام الشامل للحضور والمحاضرات')
        setting.logo_url = os.environ.get('LOGO_URL', setting.logo_url or 'https://i.top4top.io/p_3822gqcjp1.png')
        if os.environ.get('TELEGRAM_CHANNEL_URL'):
            setting.telegram_channel_url = os.environ.get('TELEGRAM_CHANNEL_URL')
        setting.save()

        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL', '')
        full_name = os.environ.get('ADMIN_FULL_NAME', 'مدير النظام')

        if username and password:
            user, _ = User.objects.get_or_create(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.first_name = full_name
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS('Production admin user is ready.'))
        else:
            self.stdout.write('ADMIN_USERNAME/ADMIN_PASSWORD not set; admin user was not created automatically.')
