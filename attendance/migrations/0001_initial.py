# Generated for Academy Attendance Platform
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180, verbose_name='اسم الدفعة')),
                ('description', models.TextField(blank=True, verbose_name='وصف مختصر')),
                ('color', models.CharField(default='#2f7d6f', max_length=20, verbose_name='لون الدفعة')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشطة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
            ],
            options={'verbose_name': 'دفعة تدريبية', 'verbose_name_plural': 'الدفعات التدريبية', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160, verbose_name='العنوان')),
                ('body', models.TextField(verbose_name='المحتوى')),
                ('audience', models.CharField(choices=[('all', 'الجميع'), ('admin', 'الإدارة فقط'), ('trainee', 'المتدربون فقط')], default='all', max_length=20, verbose_name='الفئة المستهدفة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')),
                ('is_active', models.BooleanField(default=True, verbose_name='مفعّل')),
            ],
            options={'verbose_name': 'إعلان', 'verbose_name_plural': 'الإعلانات', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SiteSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academy_name', models.CharField(default='أكاديميتي', max_length=180, verbose_name='اسم الأكاديمية')),
                ('system_name', models.CharField(default='النظام الشامل للحضور والمحاضرات', max_length=220, verbose_name='اسم النظام')),
                ('logo_url', models.URLField(default='https://i.top4top.io/p_3822gqcjp1.png', max_length=500, verbose_name='رابط الشعار')),
                ('primary_color', models.CharField(default='#2f7d6f', max_length=20, verbose_name='اللون الأساسي')),
                ('accent_color', models.CharField(default='#f2bd3a', max_length=20, verbose_name='لون التمييز')),
            ],
            options={'verbose_name': 'إعدادات الموقع', 'verbose_name_plural': 'إعدادات الموقع'},
        ),
        migrations.CreateModel(
            name='TraineeProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=180, verbose_name='الاسم الكامل')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='رقم الجوال')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التسجيل')),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainees', to='attendance.batch', verbose_name='الدفعة')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trainee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'متدرب', 'verbose_name_plural': 'المتدربون', 'ordering': ['full_name']},
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=220, verbose_name='عنوان المحاضرة')),
                ('description', models.TextField(blank=True, verbose_name='وصف المحاضرة')),
                ('date', models.DateField(verbose_name='تاريخ المحاضرة')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='وقت البداية')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='وقت النهاية')),
                ('zoom_url', models.URLField(max_length=500, verbose_name='رابط زووم')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعالة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='attendance.batch', verbose_name='الدفعة')),
            ],
            options={'verbose_name': 'محاضرة ورابط زووم', 'verbose_name_plural': 'المحاضرات وروابط الزووم', 'ordering': ['-date', '-start_time']},
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('present', 'حاضر'), ('late', 'متأخر'), ('absent', 'غائب')], default='present', max_length=20, verbose_name='الحالة')),
                ('checked_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='وقت التحضير')),
                ('zoom_url_snapshot', models.URLField(blank=True, max_length=500, verbose_name='الرابط المستخدم')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='المتصفح والجهاز')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.session', verbose_name='المحاضرة')),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.traineeprofile', verbose_name='المتدرب')),
            ],
            options={'verbose_name': 'سجل حضور', 'verbose_name_plural': 'سجلات الحضور', 'ordering': ['-checked_at'], 'unique_together': {('trainee', 'session')}},
        ),
        migrations.CreateModel(
            name='TraineeZoomLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoom_url', models.URLField(max_length=500, verbose_name='رابط زووم خاص')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_links', to='attendance.session')),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_zoom_links', to='attendance.traineeprofile')),
            ],
            options={'verbose_name': 'رابط زووم مخصص', 'verbose_name_plural': 'روابط زووم مخصصة', 'unique_together': {('session', 'trainee')}},
        ),
    ]
